from django.views import View
from django.shortcuts import render
from django.db.models import Sum, Count
from django.http import Http404, JsonResponse
from django.template.context_processors import csrf

from crispy_forms.utils import render_crispy_form

from home.utils import send_updates_webhook
from home.forms.professor_forms import ProfessorFormReview
from home.models import Professor as ProfessorModel, Review, Course, Grade
from home.tables.reviews_table import VerifiedReviewsTable
from home.forms.admin_forms import ProfessorUpdateForm, ProfessorUnverifyForm, ProfessorMergeForm


class Professor(View):
    template = "professor.html"

    def get(self, request, slug):
        professor = ProfessorModel.objects.verified.filter(slug=slug).first()
        if not professor:
            raise Http404()

        user = request.user

        review_form = ProfessorFormReview(user, professor)

        reviews = (
            Review.objects
            .verified
            .filter(professor=professor)
            .select_related("professor", "course")
            .order_by("-created_at")
        )

        reviews_table = VerifiedReviewsTable(reviews, request)

        sum, num = reviews.aggregate(sum=Sum("rating"), num=Count("rating")).values()
        average_rating = 0 if not (sum or num) else float(sum)/num

        courses_taught = Course.objects.filter(professors__pk=professor.pk)

        courses_reviewed = []
        for review in reviews:
            if review.course:
                courses_reviewed.append(review.course.name)
        courses_reviewed = set(courses_reviewed)

        grades = Grade.objects.filter(professor=professor)

        courses_graded = [grade.course.name for grade in grades]
        courses_graded = set(courses_graded)

        context = {
            "user": user,
            "professor": professor,
            "form": review_form,
            "average_rating": average_rating,
            "courses_taught": courses_taught,
            "courses_reviewed": courses_reviewed,
            "courses_graded": courses_graded,
            "reviews_table": reviews_table,
            "num_reviews": reviews.count()
        }

        if request.user.is_staff:
            edit_professor_form = ProfessorUpdateForm(professor, instance=professor)
            unverify_professor_form = ProfessorUnverifyForm(professor.pk)
            merge_professor_form = ProfessorMergeForm(request, professor)
            context["edit_professor_form"] = edit_professor_form
            context['unverify_professor_form'] = unverify_professor_form
            context['merge_professor_form'] = merge_professor_form

        return render(request, self.template, context)

    def post(self, request, slug):
        data = request.POST
        slug = data['slug']
        professor = ProfessorModel.objects.verified.filter(slug=slug).first()
        user = request.user

        form = ProfessorFormReview(user, professor, data=request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            course = Course.objects.filter(name=cleaned_data['course']).first()
            review_data = {
                "professor": professor,
                "course": course,
                "user": user if user.is_authenticated else None,
                "content": cleaned_data['content'],
                "rating": cleaned_data['rating'],
                "grade": cleaned_data['grade'],
                "anonymous": cleaned_data['anonymous']
            }

            new_review = Review(**review_data)
            new_review.save()

            send_updates_webhook(include_professors=False)

            ctx = {}
            ctx.update(csrf(request))
            form = ProfessorFormReview(user, professor)
            form_html = render_crispy_form(form, form.helper, context=ctx)

            context = {
                "success": True,
                "form": form_html
            }
        else:
            ctx = {}
            ctx.update(csrf(request))
            form_html = render_crispy_form(form, form.helper, context=ctx)

            context = {
                "success": False,
                "form": form_html
            }

        return JsonResponse(context)
