# from django.shortcuts import render
from datetime import timedelta,datetime
from rest_framework import viewsets, status, generics, mixins
from django.core import serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.core.mail import send_mail
from userauth.models import UserProfile,User
from .models import Classroom,AnswerSheet,Assignment,DoubtSection, PrivateChat, PrivateComment,Quiz,QuizTakers,Answer,Question
from .permissions import IsStudent,IsTeacher,IsTeacherOrIsStudent
from django.utils import timezone
from .serializers import ClassroomSerializer,AnswerSheetSerializer,AssignmentSerializer, DoubtSectionSerializer, PrivateChatSerializer, PrivateCommentSerializer
from userauth.permissions import IsLoggedInUserOrAdmin, IsAdminUser
from rest_framework.response import Response
from django.http import Http404
import string
import random
from . import serializers
from userauth.serializers import UserProfileSerializer
from django.forms.models import model_to_dict
from django.db.models import Q
from django.http import JsonResponse
import pytz


def get_random_string(length):
    """
    Returns Random String of given length
    """
    letters = string.ascii_lowercase + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

class ClassroomViewSet(viewsets.ModelViewSet):
    model = Classroom
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        if self.request.user.profile.is_teacher == True:
            return Classroom.objects.filter(teacher=self.request.user.profile)
        return  Classroom.objects.filter(student=self.request.user.profile)

    def create(self, request):
        data = request.data
        teacher = request.user.profile.id
        random_code = get_random_string(6)
        while(Classroom.objects.filter(class_code=random_code)) :
            random_code = get_random_string(6)
        data['class_code'] = random_code
        data['teacher'] = teacher
        data['student'] = []
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsTeacher,IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsTeacher,IsAuthenticated]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    

class ClassjoinView(APIView):
    permission_classes=[IsAuthenticated,IsStudent]

    def post(self, request, format=None):
        class_code = request.data["class_code"]
        try:
            class_join = Classroom.objects.get(class_code=class_code)
        except:
            return Response({
                "error" : "No such class.",
                "user" : request.user.email
            },status=status.HTTP_400_BAD_REQUEST)
        current_user =  request.user.profile
        class_join.student.add(current_user)
        class_join.save()
        serializer = ClassroomSerializer(class_join, context = {'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AssignmentPost(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Classroom.objects.get(pk=pk)
        except :
            raise Http404
    def get(self, request, pk, format=None):
        user_profile = request.user.profile
        classroom = self.get_object(pk)
        if user_profile == classroom.teacher or (user_profile in classroom.student.all()):
            assignment = Assignment.objects.filter(classroom=classroom)
            serializer = AssignmentSerializer(assignment,many=True,context={'request': request})
            return Response(serializer.data)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    def post(self, request, pk, format=None):
        user_profile = request.user.profile
        classroom = self.get_object(pk)
        if user_profile == classroom.teacher:
            data=request.data.copy()
            data['classroom'] = classroom.id
            try:
                if datetime.strptime(data['submit_by'],'%Y-%m-%d %H:%M:%S.%f') <= datetime.now()+timedelta(minutes=5):
                    return Response({"submit_by" : "[can not be smaller than current time + 5 minutes.]"},status=status.HTTP_400_BAD_REQUEST)
            except:
                pass
            email_list =[]
            for student in classroom.student.all():
                email_list.append(student.user.email)
            serializer = AssignmentSerializer(data=data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                send_mail(
                'SmartLearn: You got a new assignment.',
                f"Following are the details of your assignment:\n\tYour Class: {classroom.subject_name}\n\tTeacher: {classroom.teacher.name}\n\tAssignment: {data['title']}\nPlease refer to SmartLearn App for more information about this assignment.",
                'SmartLearn <nidhi.smartlearn@gmail.com>',
                email_list,
                fail_silently=False,
                )
                return Response({'assignment_id' : serializer.data['id']},status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    

class AssignmentView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk,id):
        try:
            classroom = Classroom.objects.get(pk=pk)
            assignment = Assignment.objects.get(classroom=classroom,pk=id)
            return classroom
        except :
            raise Http404
    def get(self,request,pk,id,format=None):
        classroom = self.get_object(pk,id)
        assignment = Assignment.objects.get(classroom=classroom,pk=id)
        user_profile = request.user.profile
        if user_profile == classroom.teacher or (user_profile in classroom.student.all()):
            serializer = AssignmentSerializer(assignment,context={'request': request})
            return Response(serializer.data)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def delete(self,request,pk,id,format=None):
        classroom = self.get_object(pk,id)
        assignment = Assignment.objects.get(classroom=classroom,pk=id)
        user_profile = request.user.profile
        if user_profile == classroom.teacher:
            assignment.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
  
class AnswerSheetPost(APIView):
    permission_classes = [IsAuthenticated,IsStudent]
    def post(self,request,class_id,assignment_id,format=None):
        try: 
            classroom = Classroom.objects.get(pk=class_id)
            assignment = Assignment.objects.get(pk=assignment_id)
            user_profile = request.user.profile
        except:
            raise Http404
        if user_profile in classroom.student.all():
            try:
                AnswerSheet.objects.get(assignment=assignment,student=user_profile)
            except:
                data = request.data
                if assignment.submit_by:
                    if pytz.utc.localize(datetime.now()) >= assignment.submit_by:
                        data['late_submitted'] = True
                data['student'] = user_profile.id
                data['assignment'] = assignment.id
                data['marks_scored'] = 0
                data['checked'] = False
                serializer = AnswerSheetSerializer(data=data,context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response({"id" : serializer.data['id']},status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail" : "Already submitted."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


class AnswerSheetView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, class_id,assignment_id,answer_id):
        try:
            
            classroom = Classroom.objects.get(pk=class_id)
            
            assignment = Assignment.objects.get(classroom=classroom,pk=assignment_id)
            
            answer = AnswerSheet.objects.get(assignment=assignment,pk=answer_id)
           
            return answer
        except :
            raise Http404
    
    def get(self,request,class_id,assignment_id,answer_id,format=None):
        user_profile = request.user.profile
        answer = self.get_object(class_id,assignment_id,answer_id)
        if user_profile == answer.assignment.classroom.teacher or user_profile == answer.student :
            serializer = AnswerSheetSerializer(answer,context={'request': request})
            return Response(serializer.data)
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN) 
    
    def put(self,request,class_id,assignment_id,answer_id,format=None):
        user_profile = request.user.profile
        answer = self.get_object(class_id,assignment_id,answer_id)
        if user_profile == answer.assignment.classroom.teacher:
            data=request.data
            try: 
                marks = int(data['marks_scored'])
            except:
                return Response({"detail" : "marks_scored field is required."}, status=status.HTTP_400_BAD_REQUEST)
            if int(marks) <= answer.assignment.max_marks:
                answer.marks_scored = marks
                answer.checked = True
                answer.save()
                send_mail(
                'SmartLearn: Your AnswerSheet has been checked.',
                f"Following are the details of your assignment:\n\tYour Class: {answer.assignment.classroom.subject_name}\n\tTeacher: {answer.assignment.classroom.teacher.name}\n\tAssignment: {answer.assignment.title}\nPlease refer to SmartLearn App to check your marks.",
                'SmartLearn <nidhi.smartlearn@gmail.com>',
                [answer.student.user.email,],
                fail_silently=False,
                )
                serializer = AnswerSheetSerializer(answer,context={'request': request})
                return Response({"detail" : "Answer sheet checked"},status=status.HTTP_200_OK)
            return Response({'detail': "marks_scored should not be greater that max_marks"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)  


class ListOfAnswers(APIView):
    permission_classes = [IsTeacher]
    def get_object(self, class_id,assignment_id):
        try:
            classroom = Classroom.objects.get(pk=class_id)
            assignment = Assignment.objects.get(classroom=classroom,pk=assignment_id)
            return assignment
        except:
            raise Http404
    def get(self,request,class_id,assignment_id,format=None):
        user_profile = request.user.profile
        assignment = self.get_object(class_id, assignment_id)
        print(user_profile)
        print(assignment.classroom.teacher)
        print(user_profile == assignment.classroom.teacher)
        if user_profile == assignment.classroom.teacher:
            answers = AnswerSheet.objects.filter(assignment=assignment)
            serializer = AnswerSheetSerializer(answers,many=True,context={'request': request})
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response({"detail" : "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
class PortalStudentView(APIView):
    permission_classes = [IsStudent]
    def get_class(self,class_id):
        try:
            return Classroom.objects.get(id=class_id)
        except:
            raise Http404
    def get(self,request,class_id):
        classroom = self.get_class(class_id)
        student = request.user.profile
        if student not in classroom.student.all():
            raise Http404
        all_assignments = classroom.assignment.all()
        assignment_list = []      
        percentage = 0.0
        total_marks = 0
        marks_obtained = 0
        for assignment in all_assignments:
            details ={
                'id': assignment.id,
                'assignment' : assignment.title,
                'max_marks' :assignment.max_marks,
                'submitted' : False,
                'checked' : False,
                'marks_scored' : 0,
                'due_date' : assignment.submit_by
            }
            try:
                answer = assignment.answersheet.get(student=student)
            except:
                total_marks +=assignment.max_marks
                assignment_list.append(details)
                continue
            details['submitted'] = True
            details['checked'] = answer.checked
            if answer.checked:
                total_marks+=assignment.max_marks
                marks_obtained+=answer.marks_scored
                details['marks_scored'] = answer.marks_scored
            assignment_list.append(details)
        if total_marks!=0:
            percentage = round(100*marks_obtained/total_marks,2)
        else:
            percentage = 100.00
        response = {
            'percentage' : percentage,
            'assignments' : assignment_list
        }
        return Response(response)

class DoubtSectionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, class_id):
        try:
            classroom = Classroom.objects.get(pk=class_id)
            doubts    = classroom.doubt.all()
        except:
            raise Http404

        if not(request.user.email == classroom.teacher.user.email or request.user.email in [student.user.email for student in classroom.student.all()]): 
            return Response({"Message":"You are not a participant of this Classroom"},status= status.HTTP_401_UNAUTHORIZED)
        serializer = DoubtSectionSerializer(doubts, many = True,context={'request': request})
        return Response(serializer.data, status = status.HTTP_200_OK)
        

    def post(self, request, class_id):
        data = request.data
        poster = request.user
        classroom = Classroom.objects.get(pk = class_id).id
        teacher = Classroom.objects.get(id = class_id).teacher.user.email
        students = Classroom.objects.get(id = class_id).student.all()
        data['classroom'] = classroom
        data['user'] = poster.profile.id
        if not(poster.email == teacher or poster.email in [student.user.email for student in students]):
            return Response(status= status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = DoubtSectionSerializer(data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class DoubtSectionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, class_id, doubt_id):
        try:
            doubt     = DoubtSection.objects.get(id = doubt_id)
        except:
            Http404
        if request.user.profile == doubt.user:
            doubt.delete()
            return Response({'msg':'Message deleted successfully'}, status = status.HTTP_202_ACCEPTED)
        return Response({'msg':"You can't delete doubt text of other"}, status = status.HTTP_403_FORBIDDEN)


class ClassroomDataView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,class_id,format=None):
        print(class_id)
        try:
            classroom = Classroom.objects.get(id=class_id)
            print(class_id)
        except:
            raise Http404
        if not (request.user.profile == classroom.teacher or request.user.profile in classroom.student.all()):
            return Response({"detail": "You do not have permission to perform this action."},status=status.HTTP_403_FORBIDDEN)
        students = UserProfileSerializer(classroom.student.all(),many=True,context={'request':request})
        teacher = UserProfileSerializer(classroom.teacher,context={'request':request})
        no_of_students = classroom.student.count()
        class_code = classroom.class_code
        subject_name = classroom.subject_name
        response = { 'class_code': class_code, "subject_name" : subject_name,'no_of_students' : no_of_students , 'teacher' : teacher.data, 'students' : students.data }
        return Response(response,status=status.HTTP_200_OK)


class PortalTeacherView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, class_id):
        try: 
            classroom =  Classroom.objects.get(id=class_id)
        except:
            raise Http404
        class_record          = list()
        student_record        = dict()
        unattemped_assignment = []
        unchecked_assignment  = []
        if request.user.profile == classroom.teacher:
            for student in classroom.student.all():
                total_marks  = 0
                marks_obtained = 0
                for assignment in classroom.assignment.all():
                    # total_marks  += assignment.max_marks
                    try:
                        answer = assignment.answersheet.get(student = student)
                        if answer.checked:
                            total_marks  += assignment.max_marks
                            marks_obtained += answer.marks_scored
                            continue
                        unchecked_assignment.append(AssignmentSerializer(assignment, context={'request': request}).data)
                    except:
                        total_marks  += assignment.max_marks
                        unattemped_assignment.append(AssignmentSerializer(assignment, context={'request': request}).data)
                        continue
                if not total_marks:
                    return Response({'msg':'There are no assignments in this Classroom'}, status = status.HTTP_204_NO_CONTENT)
                overall_percentage = round(marks_obtained/total_marks*100, 2)
                student_record['student']                = UserProfileSerializer(student, context={'request': request}).data  
                student_record['maximum_marks']          = total_marks
                student_record['marks_obtained']         = marks_obtained
                student_record['percentage']             = overall_percentage
                # student_record['unattemped_assignment']  = unattemped_assignment 
                # student_record['unchecked_assignment']   = unchecked_assignment  
                class_record.append(student_record.copy())
            return Response(class_record, status = status.HTTP_200_OK)
        return Response({'msg':'You dont have permission to access these records'}, status = status.HTTP_403_FORBIDDEN)


class PrivateChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get_class(self, class_id):
        try:
            return Classroom.objects.get(id = class_id)
        except:
            raise Http404

    def get_reciever(self, reciever_id):
        try:
            return UserProfile.objects.get(id = reciever_id)
        except:
            raise Http404

    def get_chat(self, class_id, reciever_id, sender_id):
        try:
            chat1 = PrivateChat.objects.filter(classroom = class_id, reciever = reciever_id, sender = sender_id )
            chat2 = PrivateChat.objects.filter(classroom = class_id, reciever = sender_id, sender = reciever_id )
            return chat1 | chat2
        except:
            return Response({"msg":"No chat history found"}, status = status.HTTP_404_NOT_FOUND)
    

    def get(self, request, class_id, reciever_id):
        sender_id    = request.user.profile.id
        data = self.get_chat(class_id, reciever_id, sender_id)
        serializer = PrivateChatSerializer(data, many = True, context={'request': request})
        return Response(serializer.data, status = status.HTTP_200_OK)

    def post(self, request, class_id, reciever_id):
        classroom = self.get_class(class_id)
        sender    = request.user
        reciever  = self.get_reciever(reciever_id)
        
        if ((sender.email == classroom.teacher.user.email or 
                sender.email in [student.user.email for student in classroom.student.all()])):

                    if (reciever.user.email == classroom.teacher.user.email or 
                            reciever.user.email in [student.user.email for student in classroom.student.all()]):

                            if (sender.email != reciever.user.email):

                                if not ((reciever.user.email in [student.user.email for student in classroom.student.all()]) and
                                        (sender.email in [student.user.email for student in classroom.student.all()])):
                                    data = request.data.copy()
                                    data['classroom'] = classroom.id
                                    data['sender']    = sender.profile.id
                                    data['reciever']  = reciever.id

                                    serializer = PrivateChatSerializer(data = data, context={'request': request})

                                    if serializer.is_valid():
                                        serializer.save()
                                        if sender.email == classroom.teacher.user.email:
                                            mail_body = f"You have a new message from your teacher {sender.profile.name} from classroom {classroom.subject_name}"
                                            send_mail('Greetings from SmartLearn Team', mail_body, 'SmartLearn<nidhi.smartlearn@gmail.com>', [reciever.user.email], fail_silently = False) 
                                            return Response(serializer.data,status=status.HTTP_200_OK)
                                        mail_body = f"You have a new message from one of you student {sender.profile.name} from classroom {classroom.subject_name}"
                                        send_mail('Greetings from SmartLearn Team', mail_body, 'SmartLearn<nidhi.smartlearn@gmail.com>', [reciever.user.email], fail_silently = False) 
                                        return Response(serializer.data,status=status.HTTP_200_OK)

                                    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    return Response({"msg":"Student can't chat with each other"}, status = status.HTTP_403_FORBIDDEN)

                            else:
                                return Response({"msg":"One can't send a message to himself"}, status = status.HTTP_403_FORBIDDEN)
                                
                    else:
                        return Response({"msg":"Reciever isn't part of the classroom"}, status = status.HTTP_403_FORBIDDEN)
        else:
            return Response({"msg":"Sender isn't part of the classroom"}, status = status.HTTP_403_FORBIDDEN)

class PrivateChatDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_chat_sender(self, chat_id):
        try:
            return PrivateChat.objects.get(pk = chat_id).sender
        except:
            Http404

    def delete(self, request, class_id, chat_id):
        sender = self.get_chat_sender(chat_id)
        request_user = request.user.profile
        if request_user == sender:
            query = PrivateChat.objects.get(id = chat_id)
            query.delete()
            return Response({'msg':'Deleted chat successfully'}, status = status.HTTP_200_OK)
        return Response({'msg':"Can't delete chat of others"}, status = status.HTTP_200_OK)
        
        
class StudentPrivateCommentOnAssignment(APIView):
    permission_classes = [IsStudent]
    def get_assignment(self,class_id,assignment_id):
        try:
            return self.request.user.profile.ClassStudent.get(id=class_id).assignment.get(id=assignment_id)#assignment has no direct relation with any userprofile
        except:
            raise Http404
    def post(self,request,class_id,assignment_id,format=None):
        assignment =self.get_assignment(class_id,assignment_id)
        teacher = assignment.classroom.teacher
        data = request.data
        data['sender'] = request.user.profile.id
        data['receiver'] = teacher.id
        data['assignment'] = assignment.id
        serilaizer = PrivateCommentSerializer(data=data,context={'request': request})
        if serilaizer.is_valid():
            serilaizer.save()
            send_mail(
            'SmartLearn: Your Student added a private comment on assignment.',
            f"Following are the details of your assignment:\n\tYour Class: {assignment.classroom.subject_name}\n\tStudent: {request.user.profile.name}\n\tAssignment: {assignment.title}\nPlease refer to SmartLearn App to check your marks.",
            'SmartLearn <nidhi.smartlearn@gmail.com>',
            [teacher.user.email,])
            return Response(serilaizer.data,status=status.HTTP_201_CREATED)
        return Response(serilaizer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request,class_id,assignment_id,format=None):
        assignment = self.get_assignment(class_id,assignment_id)
        # comments = request.user.profile.private_chat_sent.filter(assignment=assignment.id) | request.user.profile.private_chat_received.filter(assignment=assignment.id)
        comments = PrivateComment.objects.filter(Q(sender=request.user.profile.id)|Q(receiver=request.user.profile.id),assignment=assignment.id)
        serializer = PrivateCommentSerializer(comments,context={'request':request},many=True)
        return Response(serializer.data)


class TeacherPrivateCommentOnAssignment(APIView):
    permission_classes = [IsTeacher]
    def get_assignment(self,class_id,assignment_id):
        try:
            classroom = Classroom.objects.get(id=class_id)
            return Assignment.objects.get(classroom=classroom,id=assignment_id)
        except:
            raise Http404
    def get_student(self,class_id,student_id):
        try:
            classroom = Classroom.objects.get(id=class_id)
            return classroom.student.get(id=student_id)
        except:
            raise Http404
    def post(self,request,class_id,assignment_id,student_id,format=None):
        assignment = self.get_assignment(class_id,assignment_id)
        student = self.get_student(class_id,student_id)
        if request.user.profile == assignment.classroom.teacher:
            data = request.data
            data['sender'] = request.user.profile.id
            data['receiver'] = student.id
            data['assignment'] = assignment_id
            serilaizer = PrivateCommentSerializer(data=data,context={'request': request})
            if serilaizer.is_valid():
                serilaizer.save()
                send_mail(
                'SmartLearn: Teacher added a private comment on assignment.',
                f"Following are the details of your assignment:\n\tYour Class: {assignment.classroom.subject_name}\n\tTeacher: {assignment.classroom.teacher.name}\n\tAssignment: {assignment.title}\nPlease refer to SmartLearn App to check your marks.",
                'SmartLearn <nidhi.smartlearn@gmail.com>',
                [student.user.email,],)
                return Response(serilaizer.data,status=status.HTTP_201_CREATED)
            return Response(serilaizer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "You do not have permission to perform this action."},status=status.HTTP_403_FORBIDDEN)
    def get(self,request,class_id,assignment_id,student_id,format=None):
        assignment = self.get_assignment(class_id,assignment_id)
        student = self.get_student(class_id,student_id)
        if request.user.profile == assignment.classroom.teacher:
            comments = PrivateComment.objects.filter(Q(sender=student.id)|Q(receiver=student.id),assignment=assignment.id)
            serializer = PrivateCommentSerializer(comments,context={'request':request},many=True)
            return Response(serializer.data)
        else:
            Response(status=status.HTTP_403_FORBIDDEN)


class QuizView(APIView):
    permission_classes = [IsAuthenticated]
    def get_class(self,class_id):
        try:
            return Classroom.objects.get(id=class_id)
        except:
            raise Http404
    def post(self,request,class_id,format=None):
        classroom = self.get_class(class_id)
        print(request.user.profile)
        if request.user.profile != classroom.teacher:
            return Response(status=status.HTTP_403_FORBIDDEN)
        data = request.data
        print(request.data)
        data['classroom'] = classroom.id
        serializer = serializers.QuizSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request,class_id,format=None):
        classroom = self.get_class(class_id)
        if request.user.profile == classroom.teacher:
            quizzes = classroom.quiz.all()
        elif request.user.profile in classroom.student.all():
            quizzes = classroom.quiz.filter(shared=True)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = serializers.QuizSerializer(quizzes,many=True)
        return Response(serializer.data)

class AddQuestion(APIView):
    permission_classes =[IsTeacher]
    def get_quiz(self,class_id,quiz_id):
        try:
            return Quiz.objects.get(id=quiz_id,classroom=class_id)
        except:
            raise Http404
    def post(self,request,class_id,quiz_id,format=None):
        quiz = self.get_quiz(class_id,quiz_id)
        if request.user.profile != quiz.classroom.teacher:
            return Response(status=status.HTTP_403_FORBIDDEN)
        data =request.data
        data['quiz'] = quiz.id
        try:
            answer = data['answer']
        except:
            return Response({"detail":"add correct answer too."},status=status.HTTP_400_BAD_REQUEST)
        answer['is_correct'] = True
        question_serializer = serializers.QuestionSerializer(data=data)
        if question_serializer.is_valid():
            question_serializer.save()
            quiz.question_count = quiz.questions.count()
            quiz.save()
            answer['question'] = question_serializer.data['id']
            answer_serializer = serializers.ChoiceSerializer(data=answer)
            if answer_serializer.is_valid():
                answer_serializer.save() 
            return Response(question_serializer.data,status=status.HTTP_201_CREATED)
        return Response(question_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class AddOptions(APIView):
    permission_classes=[IsTeacher]
    def get_question(self,question_id):
        try:
            return Question.objects.get(id=question_id)
        except:
            raise Http404
    def post(self,request,question_id):
        question = self.get_question(question_id)
        if request.user.profile != question.quiz.classroom.teacher:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if question.answers.count() >= 4:
            return Response({'detail':"options already added."},status=status.HTTP_400_BAD_REQUEST)
        try: 
            choice1=request.data['choice1']
            choice2=request.data['choice2']
            choice3=request.data['choice3']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        choice1['question']= question.id
        choice2['question']= question.id
        choice3['question']= question.id
        serializer1 = serializers.ChoiceSerializer(data=choice1)
        serializer2 = serializers.ChoiceSerializer(data=choice2)
        serializer3 = serializers.ChoiceSerializer(data=choice3)
        if serializer1.is_valid() and serializer2.is_valid() and serializer3.is_valid():
            serializer1.save()
            serializer2.save()
            serializer3.save()
            question = serializers.QuestionSerializer(question)
            return Response(question.data,status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class ShareQuiz(APIView):
    permission_classes = [IsTeacher]
    def get_quiz(self,quiz_id):
        try:
            return Quiz.objects.get(id=quiz_id)
        except:
            raise Http404
    def post(self,request,quiz_id,format=None):
        quiz=self.get_quiz(quiz_id)
        if request.user.profile != quiz.classroom.teacher:
            return Response(status=status.HTTP_403_FORBIDDEN)
        quiz.shared=True
        quiz.save()
        email_list=[]
        for student in quiz.classroom.student.all():
            email_list.append(student.user.email)
        send_mail(
            'You have got a new quiz',
            f'Your teacher {quiz.classroom.teacher.name} shared a new quiz {quiz.name}.\n Open SmartLearn app for more information.',
            'SmartLearn <nidhi.smartlearn.gmail.com>',
            email_list,
            fail_silently=False
        )
        return Response({"detail" : "Shared"})

class SubmitQuizAnswer(APIView):
    permission_classes = [IsAuthenticated]
    def get_quiz(self,quiz_id):
        try:
            return Quiz.objects.get(id=quiz_id)
        except:
            raise Http404
    def post(self,request,quiz_id):
        quiz=self.get_quiz(quiz_id)
        if request.user.profile not in quiz.classroom.student.all():
            return response(status=status.HTTP_403_FORBIDDEN)
        if request.user.profile.quiz_taken.get(quiz=quiz_id):
            return Response({'detail':'Already submitted'},status=status.HTTP_400_BAD_REQUEST)
        answers = list(request.data)
        correct_answer = 0
        for answer in answers:
            try:
                if Answer.objects.get(id=answer).is_correct == True:
                    correct_answer +=1
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        data = {
            'student' : request.user.profile.id,
            'quiz':quiz.id,
            'correct_answers' : correct_answer
        }
        serializer = serializers.QuizTakerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    def get(self,request,quiz_id,format=None):
        quiz = self.get_quiz(quiz_id)
        if request.user.profile == quiz.classroom.teacher:
            all_answers = quiz.submitted_by.all()
            serializer = serializers.QuizTakerSerializer(all_answers,many=True,context={'request':request})
        elif request.user.profile in quiz.classroom.student.all():
            answer = quiz.submitted_by.get(student=request.user.profile)
            serializer = serializers.QuizTakerSerializer(answer,context={'request':request})
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.data)



