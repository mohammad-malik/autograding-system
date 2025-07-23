-- IMPORTANT: If you've run previous versions of this script or have existing objects,
-- you might need to DROP them first. Use with extreme caution as this DELETES ALL DATA.
-- You might need to run these DROP statements in parts, or multiple times until no errors.
-- For example, types might need to be dropped CASCADE before tables, functions after RLS policies that use them.

-- DROP TABLE IF EXISTS public.grades CASCADE;
-- DROP TABLE IF EXISTS public.submissions CASCADE;
-- DROP TABLE IF EXISTS public.answer_key_details CASCADE;
-- DROP TABLE IF EXISTS public.answer_keys CASCADE;
-- DROP TABLE IF EXISTS public.quiz_questions CASCADE;
-- DROP TABLE IF EXISTS public.quizzes CASCADE;
-- DROP TABLE IF EXISTS public.generated_content CASCADE;
-- DROP TABLE IF EXISTS public.book_chunks CASCADE;
-- DROP TABLE IF EXISTS public.books CASCADE;
-- DROP TABLE IF EXISTS public.enrollments CASCADE;
-- DROP TABLE IF EXISTS public.classes CASCADE;
-- DROP TABLE IF EXISTS public.profiles CASCADE;
-- DROP TABLE IF EXISTS public.reports CASCADE;

-- DROP TYPE IF EXISTS public.report_type CASCADE;
-- DROP TYPE IF EXISTS public.submission_status CASCADE;
-- DROP TYPE IF EXISTS public.quiz_status CASCADE;
-- DROP TYPE IF EXISTS public.generation_status CASCADE;
-- DROP TYPE IF EXISTS public.content_type CASCADE;
-- DROP TYPE IF EXISTS public.user_class_role CASCADE;

-- DROP FUNCTION IF EXISTS public.get_user_role(uuid);
-- DROP FUNCTION IF EXISTS public.can_manage_textbook_storage(text, text);
-- DROP FUNCTION IF EXISTS public.can_view_generated_content_storage(text, text);
-- DROP FUNCTION IF EXISTS public.can_view_quiz_responses_storage(text, text);
-- DROP FUNCTION IF EXISTS public.can_view_reports_storage(text, text);

-- If you get errors related to storage buckets existing, you may need to delete them via Supabase UI or:
-- DELETE FROM storage.buckets WHERE id IN ('textbook-pdfs', 'generated-content', 'quiz-responses', 'reports');


-- 1. Create Custom Types (Enums)
-- Must be created before any tables that use them

CREATE TYPE public.user_class_role AS ENUM ('student', 'ta', 'teacher');
CREATE TYPE public.content_type AS ENUM ('slides', 'quiz');
CREATE TYPE public.generation_status AS ENUM ('pending', 'complete', 'failed', 'published');
CREATE TYPE public.quiz_status AS ENUM ('draft', 'published', 'archived');
CREATE TYPE public.submission_status AS ENUM ('uploaded', 'ocr_in_progress', 'ocr_complete', 'flagged_for_review', 'grading_in_progress', 'graded', 'human_reviewed');
CREATE TYPE public.report_type AS ENUM ('student_individual', 'class_summary');


-- 2. Create Tables in Dependency Order

-- public.profiles
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
    full_name TEXT,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'student', -- 'student', 'teacher', 'ta', 'admin'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- public.classes
CREATE TABLE public.classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    created_by_user_id UUID REFERENCES public.profiles(id) NOT NULL,
    creation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- public.enrollments (References profiles and classes)
CREATE TABLE public.enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID REFERENCES public.classes(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    role_in_class public.user_class_role NOT NULL,
    enrollment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (class_id, user_id) -- A user can only be enrolled once in a class
);

-- public.books (References profiles)
CREATE TABLE public.books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    author TEXT,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pdf_storage_url TEXT NOT NULL,
    uploaded_by_user_id UUID REFERENCES public.profiles(id) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending_processing'
);

-- public.book_chunks (References books)
CREATE TABLE public.book_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES public.books(id) ON DELETE CASCADE NOT NULL,
    chunk_index INT NOT NULL,
    chapter_title TEXT,
    page_range TEXT,
    text_content TEXT, -- Store raw text for reference/re-embedding if needed
    pinecone_vector_id TEXT UNIQUE NOT NULL
);

-- public.generated_content (References books, classes, profiles)
CREATE TABLE public.generated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES public.books(id) ON DELETE SET NULL,
    class_id UUID REFERENCES public.classes(id) ON DELETE CASCADE NOT NULL,
    type public.content_type NOT NULL,
    prompt_text TEXT NOT NULL,
    generation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status public.generation_status NOT NULL DEFAULT 'pending',
    download_url TEXT,
    generated_by_user_id UUID REFERENCES public.profiles(id) NOT NULL
);

-- public.quizzes (References classes, profiles, generated_content)
CREATE TABLE public.quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    class_id UUID REFERENCES public.classes(id) ON DELETE CASCADE NOT NULL,
    creation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by_user_id UUID REFERENCES public.profiles(id) NOT NULL,
    generated_content_id UUID REFERENCES public.generated_content(id) ON DELETE SET NULL,
    status public.quiz_status NOT NULL DEFAULT 'draft'
);

-- public.quiz_questions (References quizzes)
CREATE TABLE public.quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID REFERENCES public.quizzes(id) ON DELETE CASCADE NOT NULL,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL, -- e.g., 'multiple_choice', 'short_answer', 'true_false'
    points_possible NUMERIC NOT NULL,
    order_index INT NOT NULL,
    options JSONB -- For MCQ, stores array of options e.g., [{"text": "A", "is_correct": false}, ...]
);

-- public.answer_keys (References quizzes, profiles)
CREATE TABLE public.answer_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID REFERENCES public.quizzes(id) ON DELETE CASCADE NOT NULL,
    submitted_by_user_id UUID REFERENCES public.profiles(id) NOT NULL,
    submission_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_primary BOOLEAN DEFAULT FALSE -- Changed to FALSE, as UNIQUE INDEX will set TRUE for primary
);

-- public.answer_key_details (References answer_keys, quiz_questions)
CREATE TABLE public.answer_key_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_key_id UUID REFERENCES public.answer_keys(id) ON DELETE CASCADE NOT NULL,
    question_id UUID REFERENCES public.quiz_questions(id) ON DELETE CASCADE NOT NULL,
    correct_text_or_choice TEXT NOT NULL,
    keywords TEXT[],
    grading_instructions TEXT
);

-- public.submissions (References quizzes, profiles)
CREATE TABLE public.submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID REFERENCES public.quizzes(id) ON DELETE CASCADE NOT NULL,
    student_user_id UUID REFERENCES public.profiles(id) NOT NULL,
    submission_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    image_storage_url TEXT NOT NULL, -- URL to the handwritten image in Supabase Storage
    ocr_text_content TEXT,
    ocr_confidence_score NUMERIC,
    status public.submission_status NOT NULL DEFAULT 'uploaded'
);

-- public.grades (References submissions, quiz_questions, profiles)
CREATE TABLE public.grades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID REFERENCES public.submissions(id) ON DELETE CASCADE NOT NULL,
    question_id UUID REFERENCES public.quiz_questions(id) ON DELETE CASCADE NOT NULL,
    assigned_score NUMERIC NOT NULL,
    llm_feedback TEXT,
    human_review_flag BOOLEAN DEFAULT FALSE,
    reviewed_by_user_id UUID REFERENCES public.profiles(id),
    review_date TIMESTAMP WITH TIME ZONE,
    graded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- public.reports (References quizzes, profiles)
CREATE TABLE public.reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type public.report_type NOT NULL,
    related_quiz_id UUID REFERENCES public.quizzes(id) ON DELETE CASCADE NOT NULL,
    related_student_id UUID REFERENCES public.profiles(id), -- NULL for class_summary reports
    generated_by_user_id UUID REFERENCES public.profiles(id) NOT NULL,
    generation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    report_storage_url TEXT NOT NULL UNIQUE
);


-- 3. Create Helper Functions for Database RLS & General Logic
-- Must be created before any RLS policies that use them
CREATE OR REPLACE FUNCTION public.get_user_role(user_id uuid)
RETURNS text LANGUAGE plpgsql STABLE AS $$
DECLARE
  user_role text;
BEGIN
  SELECT role INTO user_role FROM public.profiles WHERE id = user_id;
  RETURN user_role;
END;
$$;


-- 4. Create Partial Unique Indexes and Other Common Indexes
-- Must be done after tables are created, but before RLS policies on those tables (generally safer)

-- For public.answer_keys: Ensures only one primary answer key per quiz
CREATE UNIQUE INDEX idx_answer_keys_single_primary
ON public.answer_keys (quiz_id)
WHERE is_primary IS TRUE;

-- Other performance indexes
CREATE INDEX idx_profiles_role ON public.profiles (role);
CREATE INDEX idx_classes_created_by ON public.classes (created_by_user_id);
CREATE INDEX idx_enrollments_user_class ON public.enrollments (user_id, class_id);
CREATE INDEX idx_books_uploaded_by ON public.books (uploaded_by_user_id);
CREATE INDEX idx_generated_content_class_type_status ON public.generated_content (class_id, type, status);
CREATE INDEX idx_quizzes_class_created_by_status ON public.quizzes (class_id, created_by_user_id, status);
CREATE INDEX idx_quiz_questions_quiz_id ON public.quiz_questions (quiz_id);
CREATE INDEX idx_answer_keys_quiz_id ON public.answer_keys (quiz_id);
CREATE INDEX idx_answer_key_details_key_question ON public.answer_key_details (answer_key_id, question_id);
CREATE INDEX idx_submissions_quiz_student_status ON public.submissions (quiz_id, student_user_id, status);
CREATE INDEX idx_grades_submission_question ON public.grades (submission_id, question_id);
CREATE INDEX idx_reports_quiz_student_type ON public.reports (related_quiz_id, related_student_id, report_type);


-- 5. Enable RLS on all tables
-- Must be done after tables are created
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.book_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.answer_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.answer_key_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.grades ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;


-- 6. Create RLS Policies for Tables
-- Must be done after RLS is enabled and helper functions are created

-- public.profiles RLS Policies
CREATE POLICY "Users can view own profile" ON public.profiles
FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Teachers and TAs can view relevant profiles" ON public.profiles
FOR SELECT USING (
    EXISTS (
        SELECT 1
        FROM public.enrollments e
        WHERE e.user_id = public.profiles.id
        AND EXISTS (
            SELECT 1
            FROM public.enrollments teacher_e
            WHERE teacher_e.class_id = e.class_id
            AND teacher_e.user_id = auth.uid()
            AND teacher_e.role_in_class IN ('teacher', 'ta')
        )
    ) OR auth.uid() = id
);

-- public.classes RLS Policies
CREATE POLICY "Teachers can manage their classes" ON public.classes
FOR ALL USING (created_by_user_id = auth.uid() AND public.get_user_role(auth.uid()) = 'teacher');

CREATE POLICY "Enrolled users can view classes" ON public.classes
FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.classes.id AND user_id = auth.uid())
);

-- public.enrollments RLS Policies
CREATE POLICY "Teachers can manage enrollments for their classes" ON public.enrollments
FOR ALL USING (
    (public.get_user_role(auth.uid()) = 'teacher' AND (SELECT created_by_user_id FROM public.classes WHERE id = class_id) = auth.uid())
);

CREATE POLICY "Users can view their own enrollments" ON public.enrollments
FOR SELECT USING (user_id = auth.uid());


-- public.books RLS Policies
CREATE POLICY "Teachers can manage their own books" ON public.books
FOR ALL USING (uploaded_by_user_id = auth.uid() AND public.get_user_role(auth.uid()) = 'teacher');

-- public.book_chunks RLS Policies
CREATE POLICY "Teachers can read book chunks" ON public.book_chunks
FOR SELECT USING (
    public.get_user_role(auth.uid()) = 'teacher' AND
    (SELECT uploaded_by_user_id FROM public.books WHERE id = book_id) = auth.uid()
);

-- public.generated_content RLS Policies
CREATE POLICY "Teachers can manage generated content for their classes" ON public.generated_content
FOR ALL USING (
    public.get_user_role(auth.uid()) = 'teacher' AND
    generated_by_user_id = auth.uid() AND
    EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.generated_content.class_id AND user_id = auth.uid() AND role_in_class = 'teacher')
);

CREATE POLICY "Students can view published content for their classes" ON public.generated_content
FOR SELECT USING (
    public.get_user_role(auth.uid()) = 'student' AND
    status = 'published' AND
    EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.generated_content.class_id AND user_id = auth.uid() AND role_in_class = 'student')
);

-- public.quizzes RLS Policies
CREATE POLICY "Teachers and TAs can manage quizzes for their classes" ON public.quizzes
FOR ALL USING (
    (public.get_user_role(auth.uid()) IN ('teacher', 'ta')) AND
    EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.quizzes.class_id AND user_id = auth.uid() AND role_in_class IN ('teacher', 'ta'))
);

CREATE POLICY "Students can view published quizzes for their classes" ON public.quizzes
FOR SELECT USING (
    public.get_user_role(auth.uid()) = 'student' AND
    status = 'published' AND
    EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.quizzes.class_id AND user_id = auth.uid() AND role_in_class = 'student')
);

-- public.quiz_questions RLS Policies
CREATE POLICY "Teachers and TAs can manage quiz questions" ON public.quiz_questions
FOR ALL USING (
    (public.get_user_role(auth.uid()) IN ('teacher', 'ta')) AND
    EXISTS (SELECT 1 FROM public.quizzes WHERE id = quiz_id AND EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.quizzes.class_id AND user_id = auth.uid() AND role_in_class IN ('teacher', 'ta')))
);

CREATE POLICY "Students can view quiz questions for their classes" ON public.quiz_questions
FOR SELECT USING (
    public.get_user_role(auth.uid()) = 'student' AND
    EXISTS (SELECT 1 FROM public.quizzes WHERE id = quiz_id AND status = 'published' AND EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.quizzes.class_id AND user_id = auth.uid() AND role_in_class = 'student'))
);

-- public.answer_keys RLS Policies
CREATE POLICY "Teachers and TAs can manage answer keys" ON public.answer_keys
FOR ALL USING (
    (public.get_user_role(auth.uid()) IN ('teacher', 'ta')) AND
    EXISTS (SELECT 1 FROM public.quizzes WHERE id = quiz_id AND EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.quizzes.class_id AND user_id = auth.uid() AND role_in_class IN ('teacher', 'ta')))
);

-- public.answer_key_details RLS Policies
CREATE POLICY "Teachers and TAs can manage answer key details" ON public.answer_key_details
FOR ALL USING (
    (public.get_user_role(auth.uid()) IN ('teacher', 'ta')) AND
    EXISTS (SELECT 1 FROM public.answer_keys WHERE id = answer_key_id AND EXISTS (SELECT 1 FROM public.quizzes WHERE id = answer_keys.quiz_id AND EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.quizzes.class_id AND user_id = auth.uid() AND role_in_class IN ('teacher', 'ta'))))
);

-- public.submissions RLS Policies
CREATE POLICY "Students can manage their own submissions" ON public.submissions
FOR ALL USING (student_user_id = auth.uid() AND public.get_user_role(auth.uid()) = 'student');

CREATE POLICY "Teachers and TAs can manage submissions for their quizzes" ON public.submissions
FOR ALL USING (
    (public.get_user_role(auth.uid()) IN ('teacher', 'ta')) AND
    EXISTS (SELECT 1 FROM public.quizzes WHERE id = quiz_id AND EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.quizzes.class_id AND user_id = auth.uid() AND role_in_class IN ('teacher', 'ta')))
);

-- public.grades RLS Policies
CREATE POLICY "Students can view their own grades" ON public.grades
FOR SELECT USING (
    (SELECT status FROM public.submissions WHERE id = submission_id) IN ('graded', 'human_reviewed') AND
    (SELECT student_user_id FROM public.submissions WHERE id = submission_id) = auth.uid()
);

CREATE POLICY "Teachers and TAs can manage grades for their quizzes" ON public.grades
FOR ALL USING (
    (public.get_user_role(auth.uid()) IN ('teacher', 'ta')) AND
    EXISTS (SELECT 1 FROM public.submissions WHERE id = submission_id AND EXISTS (SELECT 1 FROM public.quizzes WHERE id = submissions.quiz_id AND EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = public.quizzes.class_id AND user_id = auth.uid() AND role_in_class IN ('teacher', 'ta'))))
);

-- public.reports RLS Policies
CREATE POLICY "Students can view their own individual reports" ON public.reports
FOR SELECT USING (
    report_type = 'student_individual' AND
    related_student_id = auth.uid() AND
    public.get_user_role(auth.uid()) = 'student'
);

CREATE POLICY "Teachers and TAs can view reports for their classes" ON public.reports
FOR SELECT USING (
    (public.get_user_role(auth.uid()) IN ('teacher', 'ta')) AND
    EXISTS (SELECT 1 FROM public.enrollments WHERE class_id = (SELECT class_id FROM public.quizzes WHERE id = related_quiz_id) AND user_id = auth.uid() AND role_in_class IN ('teacher', 'ta'))
);


-- 7. Create Storage Buckets
-- Must be done after the storage schema is available (which it is by default in Supabase)

INSERT INTO storage.buckets (id, name, public) VALUES ('textbook-pdfs', 'textbook-pdfs', FALSE);
INSERT INTO storage.buckets (id, name, public) VALUES ('generated-content', 'generated-content', FALSE);
INSERT INTO storage.buckets (id, name, public) VALUES ('quiz-responses', 'quiz-responses', FALSE);
INSERT INTO storage.buckets (id, name, public) VALUES ('reports', 'reports', FALSE);


-- 8. Create Helper Functions for Storage RLS Policies
-- These functions will be called directly in the Storage RLS policies to encapsulate complex logic.
-- They take the `bucket_id` and `object_name` (the full path within the bucket) as arguments.

-- Can a teacher manage a textbook object in storage?
CREATE OR REPLACE FUNCTION public.can_manage_textbook_storage(
    p_bucket_id text,
    p_object_name text
)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    RETURN (
        p_bucket_id = 'textbook-pdfs' AND
        public.get_user_role(auth.uid()) = 'teacher' AND
        EXISTS (SELECT 1 FROM public.books WHERE pdf_storage_url = p_object_name AND uploaded_by_user_id = auth.uid())
    );
END;
$$;

-- Can a student view their own quiz response image in storage?
CREATE OR REPLACE FUNCTION public.can_view_quiz_responses_storage_student(
    p_bucket_id text,
    p_object_name text
)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    RETURN (
        p_bucket_id = 'quiz-responses' AND
        public.get_user_role(auth.uid()) = 'student' AND
        EXISTS (SELECT 1 FROM public.submissions WHERE image_storage_url = p_object_name AND student_user_id = auth.uid())
    );
END;
$$;

-- Can a teacher/TA view a quiz response image for quizzes in their classes?
CREATE OR REPLACE FUNCTION public.can_view_quiz_responses_storage_teacher_ta(
    p_bucket_id text,
    p_object_name text
)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    RETURN (
        p_bucket_id = 'quiz-responses' AND
        public.get_user_role(auth.uid()) IN ('teacher', 'ta') AND
        EXISTS (
            SELECT 1
            FROM public.submissions s
            JOIN public.quizzes q ON s.quiz_id = q.id
            JOIN public.enrollments e ON q.class_id = e.class_id
            WHERE s.image_storage_url = p_object_name
            AND e.user_id = auth.uid()
            AND e.role_in_class IN ('teacher', 'ta')
        )
    );
END;
$$;

-- Can a teacher view their generated content (slides/quizzes) in storage?
CREATE OR REPLACE FUNCTION public.can_view_generated_content_storage_teacher(
    p_bucket_id text,
    p_object_name text
)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    RETURN (
        p_bucket_id = 'generated-content' AND
        public.get_user_role(auth.uid()) = 'teacher' AND
        EXISTS (SELECT 1 FROM public.generated_content WHERE download_url = p_object_name AND generated_by_user_id = auth.uid())
    );
END;
$$;

-- Can a student view published generated content (slides/quizzes) for their classes in storage?
CREATE OR REPLACE FUNCTION public.can_view_generated_content_storage_student(
    p_bucket_id text,
    p_object_name text
)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    RETURN (
        p_bucket_id = 'generated-content' AND
        public.get_user_role(auth.uid()) = 'student' AND
        EXISTS (
            SELECT 1
            FROM public.generated_content gc
            JOIN public.enrollments e ON gc.class_id = e.class_id
            WHERE gc.download_url = p_object_name
            AND gc.status = 'published'
            AND e.user_id = auth.uid()
            AND e.role_in_class = 'student'
        )
    );
END;
$$;

-- Can a student view their own reports in storage?
CREATE OR REPLACE FUNCTION public.can_view_reports_storage_student(
    p_bucket_id text,
    p_object_name text
)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    RETURN (
        p_bucket_id = 'reports' AND
        public.get_user_role(auth.uid()) = 'student' AND
        EXISTS (SELECT 1 FROM public.reports r WHERE r.report_storage_url = p_object_name AND r.related_student_id = auth.uid() AND r.report_type = 'student_individual')
    );
END;
$$;

-- Can a teacher/TA view reports for their classes in storage?
CREATE OR REPLACE FUNCTION public.can_view_reports_storage_teacher_ta(
    p_bucket_id text,
    p_object_name text
)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    RETURN (
        p_bucket_id = 'reports' AND
        public.get_user_role(auth.uid()) IN ('teacher', 'ta') AND
        EXISTS (
            SELECT 1
            FROM public.reports r
            JOIN public.quizzes q ON r.related_quiz_id = q.id
            JOIN public.enrollments e ON q.class_id = e.class_id
            WHERE r.report_storage_url = p_object_name
            AND e.user_id = auth.uid()
            AND e.role_in_class IN ('teacher', 'ta')
        )
    );
END;
$$;


-- 9. Create Storage RLS Policies (using the new helper functions)
-- Must be done after buckets and helper functions are created.

-- Policies for 'textbook-pdfs' bucket
CREATE POLICY "Teachers can manage their own textbooks (insert, update, delete)" ON storage.objects
FOR ALL USING (public.can_manage_textbook_storage(bucket_id, name)); -- Covers INSERT/UPDATE/DELETE as well due to 'ALL'


-- Policies for 'generated-content' bucket
CREATE POLICY "Teachers can upload generated content" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'generated-content' AND public.get_user_role(auth.uid()) = 'teacher'); -- Insert is simpler, can keep direct check

CREATE POLICY "Teachers can view their generated content" ON storage.objects
FOR SELECT USING (public.can_view_generated_content_storage_teacher(bucket_id, name));

CREATE POLICY "Students can view published generated content for their classes" ON storage.objects
FOR SELECT USING (public.can_view_generated_content_storage_student(bucket_id, name));


-- Policies for 'quiz-responses' bucket
CREATE POLICY "Students can upload quiz responses" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'quiz-responses' AND public.get_user_role(auth.uid()) = 'student');

CREATE POLICY "Students can view their own quiz responses" ON storage.objects
FOR SELECT USING (public.can_view_quiz_responses_storage_student(bucket_id, name));

CREATE POLICY "Teachers and TAs can view quiz responses for their quizzes" ON storage.objects
FOR SELECT USING (public.can_view_quiz_responses_storage_teacher_ta(bucket_id, name));


-- Policies for 'reports' bucket
CREATE POLICY "Teachers and TAs can upload reports" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'reports' AND public.get_user_role(auth.uid()) IN ('teacher', 'ta'));

CREATE POLICY "Students can view their own reports" ON storage.objects
FOR SELECT USING (public.can_view_reports_storage_student(bucket_id, name));

CREATE POLICY "Teachers and TAs can view reports for their classes" ON storage.objects
FOR SELECT USING (public.can_view_reports_storage_teacher_ta(bucket_id, name));