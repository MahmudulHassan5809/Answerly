from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView,DetailView,UpdateView,DayArchiveView,RedirectView,ListView
from django.http import HttpResponse
from django.utils import timezone
from django.urls.base import reverse
from django.db.models import Q

from qanda.forms import QuestionForm,AnswerForm,AnswerAcceptanceForm
from qanda.models import Question,Answer

# Create your views here.

class SearchResultsView(ListView):
	model = Question
	template_name = 'qanda/search_results.html'

	def get_queryset(self):
		query = self.request.GET.get('q')
		object_list = Question.objects.filter(Q(title__icontains=query) | Q(question__icontains=query))
		return object_list

	def get_context_data(self, **kwargs):
		context = super(SearchResultsView, self).get_context_data(**kwargs)
		context['query'] = query = self.request.GET.get('q')
		return context

class TodaysQuestionList(RedirectView):
	def get_redirect_url(self,*args,**kwargs):
		today = timezone.now()
		return reverse('qanda:daily_questions',kwargs={
			'day': today.day,
			'month': today.month,
			'year': today.year
		})

class DailyQuestionList(DayArchiveView):
	queryset = Question.objects.all()
	date_field = 'created'
	month_format = '%m'
	allow_empty = True

class UpdateAnswerAcceptance(LoginRequiredMixin,UpdateView):
	form_class = AnswerAcceptanceForm
	queryset = Answer.objects.all()

	def get_success_url(self):
		return self.object.question.get_absolute_url()

	def form_invalid(self,form):
		return HttpResponseRedirect(redirect_to=self.object.question.get_absolute_url())

class CreateAnswerView(LoginRequiredMixin,CreateView):
	form_class = AnswerForm
	template_name = 'qanda/create_answer.html'

	def get_initial(self):
		return {
			'question' : self.get_question().id,
			'user': self.request.user.id
		}

	def get_context_data(self,**kwargs):
		return super().get_context_data(question=self.get_question(),**kwargs)

	def get_success_url(self):
		return self.object.question.get_absolute_url()

	def form_valid(self,form):
		action = self.request.POST.get('action')
		if action == 'SAVE':
			return super().form_valid(form)
		elif action == 'PREVIEW':
			ctx = self.get_context_data(preview=form.cleaned_data['answer'])
			return self.render_to_response(context=ctx)
		return HttpResponseBadRequest()

	def get_question(self):
		return Question.objects.get(pk=self.kwargs['pk'])


class QuestionDetailView(DetailView):
	model = Question
	template_name = 'qanda/question_detail.html'

	ACCEPT_FORM = AnswerAcceptanceForm(initial={'accepted': True})
	REJECT_FORM = AnswerAcceptanceForm(initial={'accepted': False})

	def get_context_data(self,**kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx.update({
			'answer_form' : AnswerForm(initial = {
				'user' : self.request.user.id,
				'question': self.object.id
			})
		})

		if self.object.can_accept_answers(self.request.user):
			ctx.update({
				'accept_form': self.ACCEPT_FORM,
				'reject_form': self.REJECT_FORM
			})
		return ctx




class AskQuestionView(LoginRequiredMixin,CreateView):
	form_class = QuestionForm
	template_name = 'qanda/ask.html'

	def get_initial(self):
		return {
			'user': self.request.user.id
		}

	def form_valid(self,form):
		action = self.request.POST.get('action')
		if action == 'SAVE':
			return super().form_valid(form)
		elif action == 'PREVIEW':
			preview = Question(question = form.cleaned_data['question'],title=form.cleaned_data['title'])
			ctx = self.get_context_data(preview = preview)
			return self.render_to_response(context=ctx)
		return HttpResponseBadRequest()
