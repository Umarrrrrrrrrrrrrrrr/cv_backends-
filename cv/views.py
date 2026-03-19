"""
CV/Resume grading and enhancement API.
"""
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView

from ml.cv_grader import grade_and_enhance, grade_resume, enhance_resume
from ml.extract_text import extract_text_from_file


@method_decorator(csrf_exempt, name='dispatch')
class CVGradeView(APIView):
    """
    Grade and enhance CV/Resume.
    POST with either:
    - cv_text: raw text string
    - file: PDF or DOCX file upload
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        cv_text = None
        uploaded = None

        # Option 1: Raw text in JSON body
        if request.data.get("cv_text"):
            cv_text = request.data["cv_text"]

        # Option 2: File upload (PDF, DOCX)
        # Accept: file, resume, cv, cv_file, document
        if not cv_text and request.FILES:
            uploaded = (
                request.FILES.get("file")
                or request.FILES.get("resume")
                or request.FILES.get("cv")
                or request.FILES.get("cv_file")
                or request.FILES.get("document")
                or (list(request.FILES.values())[0] if request.FILES else None)
            )

        if uploaded:
            if not uploaded.name.lower().endswith((".pdf", ".docx", ".doc")):
                return Response(
                    {"error": "Only PDF and DOCX files are supported"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                cv_text = extract_text_from_file(uploaded)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not cv_text or not str(cv_text).strip():
            if request.FILES and uploaded:
                return Response(
                    {
                        "error": "The uploaded PDF/DOCX contains no extractable text. "
                        "This often happens with image-based PDFs (e.g. scanned documents or PDFs exported as images). "
                        "Please upload a PDF with selectable text, or paste your CV text directly."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": "Provide cv_text (string) or file (PDF/DOCX upload)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = grade_and_enhance(cv_text)
            return Response(result)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name='dispatch')
class CVGradeOnlyView(APIView):
    """Grade only (no enhancement). Returns score and grade."""
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        cv_text = request.data.get("cv_text")
        if not cv_text and request.FILES.get("file"):
            try:
                cv_text = extract_text_from_file(request.FILES["file"])
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if not cv_text or not str(cv_text).strip():
            return Response(
                {"error": "Provide cv_text or file"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            score, grade, needs_enhancement = grade_resume(cv_text)
            return Response({
                "score": score,
                "grade": grade,
                "needs_enhancement": needs_enhancement,
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class CVEnhanceView(APIView):
    """Enhance CV only (returns suggestions and enhanced version)."""
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        cv_text = request.data.get("cv_text")
        if request.FILES.get("file"):
            try:
                cv_text = extract_text_from_file(request.FILES["file"])
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not cv_text or not str(cv_text).strip():
            return Response(
                {"error": "Provide cv_text or file"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = enhance_resume(cv_text)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
