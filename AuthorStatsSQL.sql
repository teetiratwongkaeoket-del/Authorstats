-- ==========================================
-- 1. ตารางเก็บข้อมูลประเภทต่างๆ  เพื่อให้ง่ายต่อการจัดหมวดหมู่และลดการพิมพ์ผิด
-- ==========================================

-- ตารางเก็บประเภทของรายได้ (มี 2 Row คือ สำหรับยอดขาย และสำหรับโดเนท)
CREATE TABLE public.income_types (
  income_type_id integer NOT NULL DEFAULT nextval('income_types_income_type_id_seq'::regclass),
  income_type_name text NOT NULL UNIQUE, -- ใช้ UNIQUE ป้องกันไม่ให้มีชื่อประเภทรายได้ซ้ำกัน
  CONSTRAINT income_types_pkey PRIMARY KEY (income_type_id)
);

-- ตารางเก็บช่องทางที่เกิดรายได้ (เช่น 'ReadAWrite', 'MEB', 'Dek-D')
CREATE TABLE public.platforms (
  platform_id integer NOT NULL DEFAULT nextval('platforms_platform_id_seq'::regclass),
  platform_name text NOT NULL UNIQUE, -- ใช้ UNIQUE ป้องกันการพิมพ์ชื่อแพลตฟอร์มซ้ำหรือเหลื่อมล้ำ
  CONSTRAINT platforms_pkey PRIMARY KEY (platform_id)
);

-- ตารางเก็บหมวดหมู่นิยาย (เช่น 'Fantasy', 'Adventure')
CREATE TABLE public.genres (
  genre_id integer NOT NULL DEFAULT nextval('genres_genre_id_seq'::regclass),
  genre_name text NOT NULL UNIQUE, -- ใช้ UNIQUE ป้องกันชื่อหมวดหมู่ซ้ำ
  CONSTRAINT genres_pkey PRIMARY KEY (genre_id)
);


-- ==========================================
-- 2. ตารางเก็บข้อมูลเนื้อหาหลักของนิยาย (CONTENT MANAGEMENT)
-- ==========================================

-- ตารางหลัก: เก็บนิยายแต่ละเรื่อง (ทำหน้าที่เป็น Parent ให้ตอนและรายได้รวม)
CREATE TABLE public.stories (
  story_id integer NOT NULL DEFAULT nextval('stories_story_id_seq'::regclass),
  title text NOT NULL,
  description text,
  -- จำกัดสถานะให้เป็นไปตามที่กำหนดเท่านั้น (Published, Unpublished, Closed) เพื่อป้องกันข้อมูลขยะ
  status text DEFAULT 'Published'::text CHECK (status = ANY (ARRAY['published'::text, 'unpublished'::text, 'closed'::text])),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  deleted_at timestamp with time zone, -- เก็บเวลาที่ถูกลบ (Soft Delete) แทนการลบข้อมูลทิ้งจริง ๆ เพื่อรักษาความเชื่อมโยงของรายได้
  CONSTRAINT stories_pkey PRIMARY KEY (story_id)
);

-- ตารางย่อย: เก็บเนื้อหา "รายตอน" ของแต่ละเรื่อง
CREATE TABLE public.chapters (
  episode_id integer NOT NULL DEFAULT nextval('chapters_episode_id_seq'::regclass),
  story_id integer, -- FK: ชี้กลับไปที่เรื่องหลักว่าตอนนี้เป็นของเรื่องอะไร
  episode_number integer NOT NULL, -- ลำดับของตอน
  title text,
  publish_date date,
  word_count integer DEFAULT 0,
  -- จำกัดสถานะการเขียน (Draft, Proofread, Rewrite) เพื่อคุม Workflow การทำงาน
  status text DEFAULT 'Draft'::text CHECK (status = ANY (ARRAY['draft'::text, 'proofread'::text, 'rewrite'::text])),
  created_at timestamp with time zone DEFAULT now(),
  deleted_at timestamp with time zone, -- Soft Delete สำหรับตอน (เผื่อซ่อนตอน)
  CONSTRAINT chapters_pkey PRIMARY KEY (episode_id),
  CONSTRAINT episodes_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.stories(story_id)
);

-- ตารางเชื่อม (Junction Table): ใช้ผูก นิยาย เข้ากับหมวดหมู่หลายหมวด (Many-to-Many)
CREATE TABLE public.story_genres (
  story_id integer NOT NULL,
  genre_id integer NOT NULL,
  -- ใช้ Composite Key (story_id + genre_id) เป็น PK เพื่อรับประกันว่าเรื่องนึงจะไม่มีการใส่หมวดหมู่ซ้ำกัน 2 รอบ
  CONSTRAINT story_genres_pkey PRIMARY KEY (story_id, genre_id),
  CONSTRAINT story_genres_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.stories(story_id),
  CONSTRAINT story_genres_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(genre_id)
);


-- ==========================================
-- 3. REVENUE TRACKING แยกตารางรายได้ออกเป็น 2 ระดับ (ตอน กับเรื่อง) เพื่อกำจัดค่า NULL
-- ==========================================

-- ตารางรายได้ระดับเรื่อง (เช่น ยอดขายอีบุ๊กทั้งเล่ม การโดเนทแบบทั้งเรื่อง)
CREATE TABLE public.story_incomes (
  story_income_id integer NOT NULL DEFAULT nextval('story_incomes_story_income_id_seq'::regclass),
  story_id integer NOT NULL, -- FK: บังคับว่ารายได้ก้อนนี้ต้องผูกกับเรื่อง
  platform_id integer,       -- FK: มาจากแพลตฟอร์มไหน
  income_type_id integer,    -- FK: เป็นรายได้ประเภทไหน
  amount numeric NOT NULL,   -- ยอดเงิน
  income_date date DEFAULT CURRENT_DATE, -- วันที่ได้รับเงิน
  created_at timestamp with time zone DEFAULT now(),
  deleted_at timestamp with time zone,
  CONSTRAINT story_incomes_pkey PRIMARY KEY (story_income_id),
  CONSTRAINT story_incomes_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.stories(story_id),
  CONSTRAINT story_incomes_platform_id_fkey FOREIGN KEY (platform_id) REFERENCES public.platforms(platform_id),
  CONSTRAINT story_incomes_income_type_id_fkey FOREIGN KEY (income_type_id) REFERENCES public.income_types(income_type_id)
);

-- ตารางรายได้ระดับตอน (เช่น การซื้ออ่านรายตอน การโดเนทให้เฉพาะเจาะจงที่ตอนนี้)
CREATE TABLE public.chapter_incomes (
  chapter_income_id integer NOT NULL DEFAULT nextval('chapter_incomes_chapter_income_id_seq'::regclass),
  episode_id integer NOT NULL, -- FK: บังคับว่ารายได้ก้อนนี้ต้องผูกกับตอน
  platform_id integer,         -- FK: มาจากแพลตฟอร์มไหน
  income_type_id integer,      -- FK: เป็นรายได้ประเภทไหน
  amount numeric NOT NULL,     -- ยอดเงิน
  income_date date DEFAULT CURRENT_DATE, -- วันที่ได้รับเงิน
  created_at timestamp with time zone DEFAULT now(),
  deleted_at timestamp with time zone,
  CONSTRAINT chapter_incomes_pkey PRIMARY KEY (chapter_income_id),
  CONSTRAINT chapter_incomes_episode_id_fkey FOREIGN KEY (episode_id) REFERENCES public.chapters(episode_id),
  CONSTRAINT chapter_incomes_platform_id_fkey FOREIGN KEY (platform_id) REFERENCES public.platforms(platform_id),
  CONSTRAINT chapter_incomes_income_type_id_fkey FOREIGN KEY (income_type_id) REFERENCES public.income_types(income_type_id)
);