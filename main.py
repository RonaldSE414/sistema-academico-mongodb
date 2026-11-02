import os
import queue
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import customtkinter as ctk
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.server_api import ServerApi


NAVY = "#102A43"
DEEP = "#0B1E34"
BLUE = "#2E709A"
AQUA = "#22C6C7"
PALE = "#EAF9FA"
CANVAS = "#F3F7FB"
WHITE = "#FFFFFF"
INK = "#1B3048"
MUTED = "#72859A"
LINE = "#E0EAF2"
RED = "#C64553"
GREEN = "#16877C"
FONT = "Segoe UI"

COURSES = (
    "Administração",
    "Análise e Desenv. de Sistemas",
    "Ciência da Computação",
    "Direito",
    "Enfermagem",
    "Engenharia Civil",
    "Pedagogia",
    "Psicologia",
    "Outros",
)
STATUS_OPTIONS = ("Matriculado", "Trancado", "Concluído")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def validate_student(values):
    name = " ".join(str(values.get("nome", "")).split())
    enrollment = str(values.get("matricula", "")).strip().upper()
    email = str(values.get("email", "")).strip().lower()
    course = str(values.get("curso", "")).strip()
    semester_text = str(values.get("periodo", "")).strip()
    situation = str(values.get("situacao", "")).strip()
    notes = str(values.get("observacoes", "")).strip()

    if not 3 <= len(name) <= 120:
        raise ValueError("Informe o nome completo, com 3 a 120 caracteres.")
    if not re.fullmatch(r"[A-Z0-9-]{4,20}", enrollment):
        raise ValueError("A matrícula precisa ter de 4 a 20 letras, números ou hífens.")
    if email and (len(email) > 120 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)):
        raise ValueError("Informe um e-mail válido ou deixe o campo em branco.")
    if course not in COURSES:
        raise ValueError("Selecione um curso válido.")
    if not semester_text.isdecimal() or not 1 <= int(semester_text) <= 12:
        raise ValueError("O período deve ser um número de 1 a 12.")
    if situation not in STATUS_OPTIONS:
        raise ValueError("Selecione uma situação acadêmica válida.")
    if len(notes) > 500:
        raise ValueError("As observações podem ter até 500 caracteres.")

    return {
        "nome": name,
        "matricula": enrollment,
        "email": email,
        "curso": course,
        "periodo": int(semester_text),
        "situacao": situation,
        "observacoes": notes,
    }


class StudentRepository:
    def __init__(self, collection):
        self.collection = collection

    def ensure_indexes(self):
        self.collection.create_index([("matricula", ASCENDING)], unique=True, name="matricula_unica")
        self.collection.create_index([("atualizado_em", DESCENDING)])
        self.collection.create_index("curso")
        self.collection.create_index("situacao")

    def create(self, student):
        now = datetime.now(timezone.utc)
        document = {**student, "criado_em": now, "atualizado_em": now}
        return str(self.collection.insert_one(document).inserted_id)

    def get(self, student_id):
        return self.collection.find_one({"_id": self._id(student_id)})

    def update(self, student_id, student):
        payload = {**student, "atualizado_em": datetime.now(timezone.utc)}
        result = self.collection.update_one({"_id": self._id(student_id)}, {"$set": payload})
        return result.matched_count == 1

    def delete(self, student_id):
        result = self.collection.delete_one({"_id": self._id(student_id)})
        return result.deleted_count == 1

    def list_students(self, search="", course="Todos os cursos", situation="Todas as situações", page=0, per_page=10):
        query = self.build_query(search, course, situation)
        total = self.collection.count_documents(query)
        page = max(0, int(page))
        students = list(
            self.collection.find(query)
            .sort([("atualizado_em", DESCENDING), ("_id", DESCENDING)])
            .skip(page * per_page)
            .limit(per_page)
        )
        return students, total

    def recent(self, limit=5):
        return list(self.collection.find({}).sort("atualizado_em", DESCENDING).limit(limit))

    def stats(self):
        return {
            "total": self.collection.count_documents({}),
            "available": self.collection.count_documents({"situacao": "Matriculado"}),
            "borrowed": self.collection.count_documents({"situacao": "Concluído"}),
            "categories": len(self.collection.distinct("curso")),
        }

    @staticmethod
    def build_query(search, course, situation):
        query = {}
        term = search.strip()
        if len(term) > 100:
            raise ValueError("A busca deve ter no máximo 100 caracteres.")
        if term:
            escaped = re.escape(term)
            query["$or"] = [
                {"nome": {"$regex": escaped, "$options": "i"}},
                {"matricula": {"$regex": escaped, "$options": "i"}},
            ]
        if course != "Todos os cursos":
            if course not in COURSES:
                raise ValueError("Curso do filtro inválido.")
            query["curso"] = course
        if situation != "Todas as situações":
            if situation not in STATUS_OPTIONS:
                raise ValueError("Situação do filtro inválida.")
            query["situacao"] = situation
        return query

    @staticmethod
    def _id(value):
        if not ObjectId.is_valid(value):
            raise ValueError("Identificador do aluno inválido.")
        return ObjectId(value)


def connect_database():
    load_dotenv(Path(__file__).resolve().parent / ".env")
    uri = os.getenv("MONGO_URI", "").strip()
    database_name = os.getenv("MONGO_DB", "sistema_academico").strip()
    if not uri or "<" in uri or ">" in uri or "SUA_SENHA" in uri:
        raise ValueError("Configure MONGO_URI no arquivo .env antes de iniciar.")
    if not uri.startswith(("mongodb+srv://", "mongodb://")):
        raise ValueError("MONGO_URI precisa começar com mongodb+srv:// ou mongodb://.")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,60}", database_name):
        raise ValueError("Defina um nome de banco válido na variável MONGO_DB.")
    client = MongoClient(
        uri, server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10000, connectTimeoutMS=10000, socketTimeoutMS=10000
    )
    try:
        client.admin.command("ping")
        repository = StudentRepository(client[database_name]["alunos"])
        repository.ensure_indexes()
        return client, repository
    except Exception:
        client.close()
        raise


def label(parent, text, size=13, weight="normal", color=INK, **kwargs):
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(family=FONT, size=size, weight=weight),
        text_color=color,
        **kwargs,
    )


def button(parent, text, command, color=NAVY, text_color=WHITE, hover=None, height=38, width=None):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=color,
        hover_color=hover or BLUE,
        text_color=text_color,
        height=height,
        width=width or 116,
        corner_radius=11,
        font=ctk.CTkFont(family=FONT, size=12, weight="bold"),
    )


def compact(text, limit=40):
    return text if len(text) <= limit else f"{text[: limit - 1]}…"


class StudentForm(ctk.CTkToplevel):
    def __init__(self, master, student=None):
        super().__init__(master)
        self.master_app = master
        self.student = student
        self.title("Editar aluno" if student else "Cadastrar aluno")
        self.configure(fg_color=CANVAS)
        self.geometry("640x740")
        self.minsize(555, 680)
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        heading = ctk.CTkFrame(self, fg_color=NAVY, corner_radius=0, height=118)
        heading.grid(row=0, column=0, sticky="ew")
        heading.grid_propagate(False)
        label(heading, "SECRETARIA  /  REGISTRO", 11, "bold", AQUA).pack(anchor="w", padx=28, pady=(20, 1))
        label(heading, "Editar aluno" if student else "Novo aluno", 24, "bold", WHITE).pack(anchor="w", padx=28)
        label(heading, "Dados armazenados diretamente no MongoDB Atlas.", 12, color="#B6CADB").pack(anchor="w", padx=28, pady=(2, 0))

        content = ctk.CTkScrollableFrame(self, fg_color=CANVAS, corner_radius=0)
        content.grid(row=1, column=0, sticky="nsew", padx=22, pady=(15, 5))
        content.grid_columnconfigure(0, weight=1)

        self.name_entry = self._entry(content, "Nome completo *", "Ex.: Maria Oliveira", 0)
        self.enrollment_entry = self._entry(content, "Matrícula *", "Ex.: 20260015", 1)
        self.email_entry = self._entry(content, "E-mail institucional ou pessoal (opcional)", "Ex.: maria@exemplo.com", 2)

        pair = ctk.CTkFrame(content, fg_color="transparent")
        pair.grid(row=3, column=0, sticky="ew", pady=(0, 14))
        pair.grid_columnconfigure((0, 1), weight=1, uniform="half")
        label(pair, "Curso *", 12, "bold").grid(row=0, column=0, sticky="w", pady=(0, 6))
        label(pair, "Período *", 12, "bold").grid(row=0, column=1, sticky="w", padx=(12, 0), pady=(0, 6))
        self.course = ctk.CTkComboBox(
            pair, values=list(COURSES), state="readonly", height=42,
            fg_color=WHITE, border_color=LINE, button_color=NAVY,
            button_hover_color=BLUE, dropdown_fg_color=WHITE,
            text_color=INK, font=(FONT, 12)
        )
        self.course.grid(row=1, column=0, sticky="ew")
        self.semester_entry = ctk.CTkEntry(
            pair, placeholder_text="1 a 12", height=42, corner_radius=9,
            border_color=LINE, fg_color=WHITE, text_color=INK, font=(FONT, 12)
        )
        self.semester_entry.grid(row=1, column=1, sticky="ew", padx=(12, 0))

        label(content, "Situação acadêmica *", 12, "bold").grid(row=4, column=0, sticky="w", pady=(0, 6))
        self.situation = ctk.CTkSegmentedButton(
            content, values=list(STATUS_OPTIONS), selected_color=AQUA,
            selected_hover_color=BLUE, unselected_color="#E7EDF3",
            unselected_hover_color="#D7E5ED", text_color=INK,
            font=ctk.CTkFont(family=FONT, size=12, weight="bold"), height=42, corner_radius=9
        )
        self.situation.grid(row=5, column=0, sticky="ew", pady=(0, 15))

        label(content, "Observações (opcional)", 12, "bold").grid(row=6, column=0, sticky="w", pady=(0, 6))
        self.notes = ctk.CTkTextbox(
            content, height=76, corner_radius=9, border_width=1,
            border_color=LINE, fg_color=WHITE, text_color=INK,
            font=(FONT, 12), wrap="word"
        )
        self.notes.grid(row=7, column=0, sticky="ew")
        label(content, "* Campos obrigatórios. Matrícula única. Observações até 500 caracteres.", 11, color=MUTED).grid(
            row=8, column=0, sticky="w", pady=(7, 8)
        )
        self.error = label(content, "", 12, color=RED, wraplength=520, justify="left")
        self.error.grid(row=9, column=0, sticky="w", pady=(0, 5))

        footer = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=79)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        self.save_btn = button(
            footer, "Salvar alterações" if student else "Cadastrar aluno",
            self.save, AQUA, NAVY, "#14ADB5", 43, 165
        )
        self.save_btn.pack(side="right", padx=(8, 24), pady=18)
        button(footer, "Cancelar", self.destroy, "#ECF2F7", INK, "#DAE5EF", 43, 108).pack(
            side="right", pady=18
        )

        self.course.set(student.get("curso", COURSES[0]) if student else COURSES[0])
        self.situation.set(student.get("situacao", STATUS_OPTIONS[0]) if student else STATUS_OPTIONS[0])
        if student:
            self.name_entry.insert(0, student.get("nome", ""))
            self.enrollment_entry.insert(0, student.get("matricula", ""))
            self.email_entry.insert(0, student.get("email", ""))
            self.semester_entry.insert(0, str(student.get("periodo", "")))
            self.notes.insert("1.0", student.get("observacoes", ""))
        self.after(140, self._focus)

    def _focus(self):
        if self.winfo_exists():
            self.grab_set()
            self.name_entry.focus_set()

    def _entry(self, parent, title, placeholder, row):
        area = ctk.CTkFrame(parent, fg_color="transparent")
        area.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        area.grid_columnconfigure(0, weight=1)
        label(area, title, 12, "bold").grid(row=0, column=0, sticky="w", pady=(0, 5))
        field = ctk.CTkEntry(
            area, placeholder_text=placeholder, height=42, corner_radius=9,
            border_color=LINE, fg_color=WHITE, text_color=INK, font=(FONT, 12)
        )
        field.grid(row=1, column=0, sticky="ew")
        return field

    def save(self):
        values = {
            "nome": self.name_entry.get(),
            "matricula": self.enrollment_entry.get(),
            "email": self.email_entry.get(),
            "curso": self.course.get(),
            "periodo": self.semester_entry.get(),
            "situacao": self.situation.get(),
            "observacoes": self.notes.get("1.0", "end-1c"),
        }
        try:
            data = validate_student(values)
        except ValueError as exc:
            self.error.configure(text=str(exc))
            return
        self.error.configure(text="")
        self.save_btn.configure(state="disabled", text="Salvando...")
        self.master_app.save_student(self.student, data, self)

    def recover(self, message="Não foi possível salvar. Confira a conexão."):
        if self.winfo_exists():
            self.save_btn.configure(
                state="normal", text="Salvar alterações" if self.student else "Cadastrar aluno"
            )
            self.error.configure(text=message)


class ConfirmDelete(ctk.CTkToplevel):
    def __init__(self, master, student):
        super().__init__(master)
        self.master_app = master
        self.student = student
        self.title("Confirmar exclusão")
        self.geometry("435x275")
        self.resizable(False, False)
        self.configure(fg_color=WHITE)
        self.transient(master)
        panel = ctk.CTkFrame(self, fg_color=WHITE)
        panel.pack(fill="both", expand=True, padx=25, pady=20)
        label(panel, "Excluir este aluno?", 22, "bold", NAVY).pack(anchor="w", pady=(3, 7))
        label(
            panel, f"{compact(student['nome'], 46)} será removido do banco de dados.",
            13, color=MUTED, wraplength=365, justify="left"
        ).pack(anchor="w", pady=(0, 10))
        label(panel, "Esta ação não poderá ser desfeita.", 12, color=RED).pack(anchor="w")
        self.error = label(panel, "", 11, color=RED)
        self.error.pack(anchor="w", pady=(5, 0))
        footer = ctk.CTkFrame(panel, fg_color="transparent")
        footer.pack(side="bottom", fill="x", pady=(10, 0))
        self.confirm_button = button(footer, "Sim, excluir", self.confirm, RED, WHITE, "#A62F42", 41, 127)
        self.confirm_button.pack(side="right")
        button(footer, "Cancelar", self.destroy, "#ECF2F7", INK, "#DCE7EF", 41, 100).pack(
            side="right", padx=(0, 9)
        )
        self.after(140, self._focus)

    def _focus(self):
        if self.winfo_exists():
            self.grab_set()

    def confirm(self):
        self.confirm_button.configure(state="disabled", text="Excluindo...")
        self.master_app.delete_student(self.student, self)

    def recover(self):
        if self.winfo_exists():
            self.confirm_button.configure(state="normal", text="Sim, excluir")
            self.error.configure(text="Não foi possível excluir. Tente novamente.")


class AcademicoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aurora | Sistema Acadêmico")
        self.geometry("1220x790")
        self.minsize(1050, 680)
        self.configure(fg_color=CANVAS)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.executor = ThreadPoolExecutor(max_workers=1)
        self.events = queue.Queue()
        self.client = None
        self.repository = None
        self.page = "dashboard"
        self.page_number = 0
        self.current_query = ("", "Todos os cursos", "Todas as situações")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._sidebar()
        self._main_area()
        self.after(100, self._poll)
        self.after(220, self.connect)

    def _sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=DEEP, corner_radius=0, width=240)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(8, weight=1)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=22, pady=(29, 30))
        mark = ctk.CTkFrame(brand, fg_color=AQUA, corner_radius=13, width=47, height=47)
        mark.pack(side="left", padx=(0, 12))
        mark.pack_propagate(False)
        label(mark, "A", 27, "bold", DEEP).pack(expand=True)
        company = ctk.CTkFrame(brand, fg_color="transparent")
        company.pack(side="left")
        label(company, "AURORA", 19, "bold", WHITE).pack(anchor="w")
        label(company, "GESTÃO ACADÊMICA", 9, "bold", "#85ADC2").pack(anchor="w")

        label(self.sidebar, "MENU PRINCIPAL", 10, "bold", "#6E91AA").grid(
            row=1, column=0, sticky="w", padx=25, pady=(0, 12)
        )
        self.nav_buttons = {}
        for i, (key, text, glyph) in enumerate(
            [("dashboard", "Painel geral", "▦"), ("catalog", "Alunos", "≡"), ("about", "Sobre o projeto", "ⓘ")], start=2
        ):
            item = ctk.CTkButton(
                self.sidebar, text=f"   {glyph}    {text}", anchor="w", height=46,
                corner_radius=10, fg_color="transparent", hover_color="#183A54",
                text_color="#C7D6E3", font=ctk.CTkFont(family=FONT, size=13, weight="bold"),
                command=lambda p=key: self.navigate(p)
            )
            item.grid(row=i, column=0, sticky="ew", padx=14, pady=4)
            self.nav_buttons[key] = item

        tip = ctk.CTkFrame(self.sidebar, fg_color="#18364C", corner_radius=14)
        tip.grid(row=9, column=0, sticky="ew", padx=16, pady=(10, 14))
        label(tip, "CONTROLE ACADÊMICO", 11, "bold", AQUA).pack(anchor="w", padx=15, pady=(15, 4))
        label(tip, "Gerencie matrículas e acompanhe cada situação acadêmica.", 11, color="#B1C7D8", wraplength=181, justify="left").pack(
            anchor="w", padx=15, pady=(0, 16)
        )
        self.connection_label = label(self.sidebar, "●  Conectando ao Atlas...", 11, color="#A5BFD2")
        self.connection_label.grid(row=10, column=0, sticky="w", padx=24, pady=(0, 22))

    def _main_area(self):
        self.main = ctk.CTkFrame(self, fg_color=CANVAS, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self.main, fg_color=WHITE, corner_radius=0, height=75)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        label(top, "GESTÃO ACADÊMICA", 11, "bold", BLUE).pack(side="left", padx=33)
        self.top_status = label(top, "MongoDB Atlas  •  Verificando conexão", 11, color=MUTED)
        self.top_status.pack(side="right", padx=30)

        self.body = ctk.CTkFrame(self.main, fg_color=CANVAS, corner_radius=0)
        self.body.grid(row=1, column=0, sticky="nsew", padx=30, pady=24)
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(0, weight=1)

        self.bottom_status = label(self.main, "Preparando o ambiente...", 11, color=MUTED)
        self.bottom_status.grid(row=2, column=0, sticky="w", padx=32, pady=(0, 12))
        self.navigate("dashboard")

    def _poll(self):
        try:
            while True:
                future, callback, on_error = self.events.get_nowait()
                try:
                    result = future.result()
                except Exception as exc:
                    self.bottom_status.configure(text=f"Falha: {exc.__class__.__name__}. Verifique a conexão e tente novamente.", text_color=RED)
                    if on_error:
                        on_error(exc)
                else:
                    callback(result)
        except queue.Empty:
            pass
        if self.winfo_exists():
            self.after(90, self._poll)

    def run_job(self, task, callback, on_error=None):
        future = self.executor.submit(task)
        future.add_done_callback(lambda completed: self.events.put((completed, callback, on_error)))

    def connect(self):
        self.connection_label.configure(text="●  Conectando ao Atlas...", text_color="#A5BFD2")
        self.top_status.configure(text="MongoDB Atlas  •  Conectando")
        self.bottom_status.configure(text="Verificando o acesso ao banco de dados...")

        def completed(result):
            self.client, self.repository = result
            self.connection_label.configure(text="●  Banco conectado", text_color=AQUA)
            self.top_status.configure(text="MongoDB Atlas  •  Online", text_color=GREEN)
            self.bottom_status.configure(text="Conexão estabelecida. Sistema pronto para uso.", text_color=MUTED)
            self.navigate(self.page)

        def failed(exc):
            self.connection_label.configure(text="●  Sem conexão", text_color="#FFB3BA")
            self.top_status.configure(text="MongoDB Atlas  •  Desconectado", text_color=RED)
            if isinstance(exc, ValueError):
                hint = str(exc)
            elif isinstance(exc, DuplicateKeyError):
                hint = "Há matrículas repetidas no banco. Confira os registros no Atlas."
            else:
                hint = "Verifique a internet, a lista de IPs, o usuário e a senha do Atlas."
            self._error_page(hint)

        self.run_job(connect_database, completed, failed)

    def clear_body(self):
        for row in range(4):
            self.body.grid_rowconfigure(row, weight=0)
        for widget in self.body.winfo_children():
            widget.destroy()

    def navigate(self, page):
        self.page = page
        for key, nav in self.nav_buttons.items():
            selected = key == page
            nav.configure(fg_color="#1B4259" if selected else "transparent", text_color=AQUA if selected else "#C7D6E3")
        self.clear_body()
        if self.repository is None:
            self._loading_page()
            return
        if page == "dashboard":
            self._dashboard()
        elif page == "catalog":
            self._catalog()
        else:
            self._about()

    def _loading_page(self):
        frame = ctk.CTkFrame(self.body, fg_color=WHITE, corner_radius=18)
        frame.grid(row=0, column=0, sticky="nsew")
        label(frame, "Conectando ao MongoDB Atlas", 25, "bold", NAVY).pack(pady=(115, 12))
        label(frame, "Preparando as informações acadêmicas.", 14, color=MUTED).pack()
        self.loading_bar = ctk.CTkProgressBar(frame, mode="indeterminate", progress_color=AQUA, width=260)
        self.loading_bar.pack(pady=30)
        self.loading_bar.start()

    def _error_page(self, description):
        self.clear_body()
        frame = ctk.CTkFrame(self.body, fg_color=WHITE, corner_radius=18)
        frame.grid(row=0, column=0, sticky="nsew")
        label(frame, "Não foi possível acessar o banco", 26, "bold", NAVY).pack(pady=(100, 15))
        label(
            frame,
            "Confira a URL no arquivo .env, a senha do usuário de banco e o acesso de rede no Atlas.",
            14, color=MUTED, wraplength=590, justify="center"
        ).pack(padx=30)
        label(frame, compact(description, 150), 12, color=RED, wraplength=600, justify="center").pack(padx=30, pady=17)
        button(frame, "Tentar novamente", self.connect, AQUA, NAVY, "#15ADB1", 45, 170).pack(pady=12)

    def _heading(self, kicker, heading, subtitle, action_text=None, action=None):
        area = ctk.CTkFrame(self.body, fg_color="transparent")
        area.grid(row=0, column=0, sticky="ew", pady=(0, 17))
        area.grid_columnconfigure(0, weight=1)
        inner = ctk.CTkFrame(area, fg_color="transparent")
        inner.grid(row=0, column=0, sticky="w")
        label(inner, kicker, 10, "bold", BLUE).pack(anchor="w")
        label(inner, heading, 27, "bold", NAVY).pack(anchor="w", pady=(3, 2))
        label(inner, subtitle, 12, color=MUTED).pack(anchor="w")
        if action_text:
            button(area, action_text, action, AQUA, NAVY, "#16B1BA", 43, 155).grid(row=0, column=1, sticky="e")
        return area

    def _dashboard(self):
        self.body.grid_rowconfigure(0, weight=0)
        self._heading("VISÃO GERAL", "Sua instituição em um só lugar", "Acompanhe os alunos e suas situações acadêmicas.", "+  Novo aluno", self.open_new)

        hero = ctk.CTkFrame(self.body, fg_color=NAVY, corner_radius=18, height=127)
        hero.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        hero.grid_propagate(False)
        label(hero, "BEM-VINDO AO AURORA", 11, "bold", AQUA).pack(anchor="w", padx=27, pady=(19, 3))
        label(hero, "Gestão de alunos, simples e organizada.", 21, "bold", WHITE).pack(anchor="w", padx=27)
        label(hero, "Registros acadêmicos armazenados no MongoDB Atlas.", 12, color="#B8CEDC").pack(anchor="w", padx=27, pady=(4, 0))

        metric_row = ctk.CTkFrame(self.body, fg_color="transparent")
        metric_row.grid(row=2, column=0, sticky="ew")
        metric_row.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="metric")
        self.metric_values = {}
        for index, (key, title, detail) in enumerate([
            ("total", "Total de alunos", "Registros cadastrados"),
            ("available", "Matriculados", "Com matrícula ativa"),
            ("borrowed", "Concluídos", "Formação concluída"),
            ("categories", "Cursos", "Áreas cadastradas"),
        ]):
            card = ctk.CTkFrame(metric_row, fg_color=WHITE, corner_radius=15, border_width=1, border_color=LINE)
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 6, 0 if index == 3 else 6))
            label(card, title, 12, "bold", MUTED).pack(anchor="w", padx=17, pady=(15, 1))
            value = label(card, "—", 30, "bold", NAVY)
            value.pack(anchor="w", padx=17)
            label(card, detail, 10, color=BLUE).pack(anchor="w", padx=17, pady=(0, 15))
            self.metric_values[key] = value

        recent_card = ctk.CTkFrame(self.body, fg_color=WHITE, corner_radius=16, border_width=1, border_color=LINE)
        recent_card.grid(row=3, column=0, sticky="nsew", pady=(19, 0))
        self.body.grid_rowconfigure(3, weight=1)
        recent_card.grid_columnconfigure(0, weight=1)
        recent_header = ctk.CTkFrame(recent_card, fg_color="transparent")
        recent_header.grid(row=0, column=0, sticky="ew", padx=21, pady=(15, 8))
        label(recent_header, "Atualizações recentes", 17, "bold", NAVY).pack(side="left")
        button(recent_header, "Ver cadastro", lambda: self.navigate("catalog"), "#EBF8FA", NAVY, "#D8F0F2", 33, 112).pack(side="right")
        self.recent_frame = ctk.CTkScrollableFrame(recent_card, fg_color="transparent", corner_radius=0)
        self.recent_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 12))
        recent_card.grid_rowconfigure(1, weight=1)
        label(self.recent_frame, "Buscando alunos...", 13, color=MUTED).pack(pady=35)

        self.run_job(lambda: (self.repository.stats(), self.repository.recent()), self._fill_dashboard)

    def _fill_dashboard(self, data):
        if self.page != "dashboard":
            return
        stats, recent = data
        for key, value in stats.items():
            self.metric_values[key].configure(text=str(value))
        for widget in self.recent_frame.winfo_children():
            widget.destroy()
        if not recent:
            label(self.recent_frame, "Nenhum aluno cadastrado. Clique em ‘Novo aluno’ para começar.", 13, color=MUTED).pack(pady=28)
            return
        for item in recent:
            row = ctk.CTkFrame(self.recent_frame, fg_color="#F7FAFD", corner_radius=11, height=55)
            row.pack(fill="x", pady=4)
            label(row, compact(item.get("nome", "Sem nome"), 47), 13, "bold", NAVY).pack(side="left", padx=(15, 7), pady=13)
            label(row, compact(item.get("matricula", ""), 31), 11, color=MUTED).pack(side="left", pady=13)
            situacao = item.get("situacao", "")
            label(row, situacao, 11, "bold", GREEN if situacao == "Matriculado" else BLUE).pack(side="right", padx=15, pady=13)

    def _catalog(self):
        self.body.grid_rowconfigure(0, weight=0)
        self.body.grid_rowconfigure(3, weight=1)
        self._heading("SECRETARIA ACADÊMICA", "Alunos matriculados", "Consulte, filtre e gerencie todos os registros.", "+  Novo aluno", self.open_new)

        filters = ctk.CTkFrame(self.body, fg_color=WHITE, corner_radius=15, border_width=1, border_color=LINE)
        filters.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        filters.grid_columnconfigure(0, weight=3)
        filters.grid_columnconfigure((1, 2), weight=2)

        search_frame = ctk.CTkFrame(filters, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=(17, 8), pady=(12, 14))
        label(search_frame, "Buscar por nome ou matrícula", 11, "bold", MUTED).pack(anchor="w", pady=(0, 5))
        self.search_entry = ctk.CTkEntry(search_frame, height=39, fg_color="#F7FAFD", border_color=LINE,
                                         text_color=INK, placeholder_text="Nome ou matrícula...", font=(FONT, 12))
        self.search_entry.pack(fill="x")
        self.search_entry.insert(0, self.current_query[0])
        self.search_entry.bind("<Return>", lambda _event: self.apply_filters())

        category_frame = ctk.CTkFrame(filters, fg_color="transparent")
        category_frame.grid(row=0, column=1, sticky="ew", padx=8, pady=(12, 14))
        label(category_frame, "Curso", 11, "bold", MUTED).pack(anchor="w", pady=(0, 5))
        self.course_filter = ctk.CTkComboBox(
            category_frame, values=["Todos os cursos", *COURSES], state="readonly", height=39,
            fg_color="#F7FAFD", border_color=LINE, button_color=NAVY, dropdown_fg_color=WHITE,
            button_hover_color=BLUE, font=(FONT, 11)
        )
        self.course_filter.pack(fill="x")
        self.course_filter.set(self.current_query[1])

        situation_frame = ctk.CTkFrame(filters, fg_color="transparent")
        situation_frame.grid(row=0, column=2, sticky="ew", padx=8, pady=(12, 14))
        label(situation_frame, "Situação", 11, "bold", MUTED).pack(anchor="w", pady=(0, 5))
        self.situation_filter = ctk.CTkComboBox(
            situation_frame, values=["Todas as situações", *STATUS_OPTIONS], state="readonly", height=39,
            fg_color="#F7FAFD", border_color=LINE, button_color=NAVY, dropdown_fg_color=WHITE,
            button_hover_color=BLUE, font=(FONT, 11)
        )
        self.situation_filter.pack(fill="x")
        self.situation_filter.set(self.current_query[2])

        actions = ctk.CTkFrame(filters, fg_color="transparent")
        actions.grid(row=0, column=3, sticky="se", padx=(8, 17), pady=(12, 14))
        button(actions, "Buscar", self.apply_filters, NAVY, WHITE, BLUE, 39, 77).pack(side="left", padx=(0, 6))
        button(actions, "Limpar", self.reset_filters, "#EDF3F7", NAVY, "#DDE9F0", 39, 74).pack(side="left")

        bar = ctk.CTkFrame(self.body, fg_color="transparent")
        bar.grid(row=2, column=0, sticky="ew", pady=(0, 7))
        self.result_label = label(bar, "Carregando registros...", 12, "bold", NAVY)
        self.result_label.pack(side="left")
        label(bar, "Resultados armazenados no Atlas", 11, color=MUTED).pack(side="right")

        table = ctk.CTkFrame(self.body, fg_color=WHITE, corner_radius=15, border_width=1, border_color=LINE)
        table.grid(row=3, column=0, sticky="nsew")
        table.grid_columnconfigure(0, weight=1)
        table.grid_rowconfigure(1, weight=1)

        columns = ctk.CTkFrame(table, fg_color="#EAF2F7", height=42, corner_radius=8)
        columns.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))
        columns.grid_propagate(False)
        self._columns(columns)
        for idx, name in enumerate(["ALUNO / MATRÍCULA", "CURSO", "PERÍODO", "SITUAÇÃO", "AÇÕES"]):
            label(columns, name, 10, "bold", BLUE, anchor="w").grid(row=0, column=idx, sticky="ew", padx=(12, 4), pady=11)

        self.rows = ctk.CTkScrollableFrame(table, fg_color=WHITE, corner_radius=0)
        self.rows.grid(row=1, column=0, sticky="nsew", padx=8, pady=6)
        self.rows.grid_columnconfigure(0, weight=1)

        pager = ctk.CTkFrame(table, fg_color="transparent", height=55)
        pager.grid(row=2, column=0, sticky="ew", padx=17, pady=(0, 10))
        self.page_info = label(pager, "Página 1", 11, color=MUTED)
        self.page_info.pack(side="left", pady=10)
        self.next_btn = button(pager, "Próxima  ›", lambda: self.change_page(1), "#EDF4F8", NAVY, "#DDEAF2", 33, 94)
        self.next_btn.pack(side="right", pady=4)
        self.prev_btn = button(pager, "‹  Anterior", lambda: self.change_page(-1), "#EDF4F8", NAVY, "#DDEAF2", 33, 94)
        self.prev_btn.pack(side="right", padx=(0, 8), pady=4)
        self.refresh_students()

    def _columns(self, frame):
        for idx, weight in enumerate((5, 3, 1, 2, 3)):
            frame.grid_columnconfigure(idx, weight=weight, uniform=None)

    def apply_filters(self):
        self.current_query = (self.search_entry.get(), self.course_filter.get(), self.situation_filter.get())
        self.page_number = 0
        self.refresh_students()

    def reset_filters(self):
        self.current_query = ("", "Todos os cursos", "Todas as situações")
        self.page_number = 0
        self.search_entry.delete(0, "end")
        self.course_filter.set(self.current_query[1])
        self.situation_filter.set(self.current_query[2])
        self.refresh_students()

    def change_page(self, delta):
        self.page_number = max(0, self.page_number + delta)
        self.refresh_students()

    def refresh_students(self):
        if self.page != "catalog":
            return
        term, course, situation = self.current_query
        page = self.page_number
        self.result_label.configure(text="Consultando o cadastro...")
        try:
            self.repository.build_query(term, course, situation)
        except ValueError as exc:
            self.result_label.configure(text=str(exc), text_color=RED)
            return
        self.run_job(
            lambda: self.repository.list_students(term, course, situation, page, 10),
            lambda result: self._fill_catalog(result, page),
            lambda _exc: self.result_label.configure(text="Erro ao consultar os alunos. Tente novamente.", text_color=RED) if self.page == "catalog" else None,
        )

    def _fill_catalog(self, result, page):
        if self.page != "catalog" or page != self.page_number:
            return
        students, total = result
        for child in self.rows.winfo_children():
            child.destroy()
        self.result_label.configure(text=f"{total} aluno(s) encontrado(s)", text_color=NAVY)
        count_pages = max(1, (total + 9) // 10)
        if page >= count_pages:
            self.page_number = count_pages - 1
            self.refresh_students()
            return
        self.page_info.configure(text=f"Página {page + 1} de {count_pages}  •  Até 10 alunos por página")
        self.prev_btn.configure(state="normal" if page > 0 else "disabled")
        self.next_btn.configure(state="normal" if (page + 1) * 10 < total else "disabled")
        if not students:
            empty = ctk.CTkFrame(self.rows, fg_color="transparent")
            empty.grid(row=0, column=0, sticky="ew", pady=64)
            label(empty, "Nenhum aluno encontrado", 20, "bold", NAVY).pack()
            label(empty, "Cadastre um aluno ou ajuste os filtros da pesquisa.", 12, color=MUTED).pack(pady=8)
            return
        for index, student in enumerate(students):
            row = ctk.CTkFrame(self.rows, fg_color=WHITE if index % 2 else "#F7FAFD", corner_radius=9, height=69)
            row.grid(row=index, column=0, sticky="ew", pady=3, padx=4)
            row.grid_propagate(False)
            self._columns(row)
            title_cell = ctk.CTkFrame(row, fg_color="transparent")
            title_cell.grid(row=0, column=0, sticky="ew", padx=(12, 3), pady=9)
            label(title_cell, compact(student.get("nome", ""), 32), 12, "bold", NAVY, anchor="w").pack(anchor="w")
            label(title_cell, compact(student.get("matricula", ""), 35), 11, color=MUTED, anchor="w").pack(anchor="w")
            label(row, compact(student.get("curso", ""), 16), 11, color=INK, anchor="w").grid(row=0, column=1, sticky="ew", padx=(12, 4))
            label(row, str(student.get("periodo", "")), 11, color=INK, anchor="w").grid(row=0, column=2, sticky="ew", padx=(12, 4))
            situacao = student.get("situacao", "")
            badge = ctk.CTkFrame(row, fg_color="#E2F5EE" if situacao == "Matriculado" else "#E6F0FA", corner_radius=8)
            badge.grid(row=0, column=3, sticky="w", padx=(9, 4))
            label(badge, situacao, 10, "bold", GREEN if situacao == "Matriculado" else BLUE).pack(padx=9, pady=7)
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=4, sticky="w", padx=(6, 4))
            button(actions, "Editar", lambda b=student: self.open_edit(b), "#E5F6F7", NAVY, "#CBEDEF", 32, 65).pack(side="left", padx=(0, 5))
            button(actions, "Excluir", lambda b=student: ConfirmDelete(self, b), "#FFF0F1", RED, "#FFE0E3", 32, 67).pack(side="left")

    def _about(self):
        self.body.grid_rowconfigure(0, weight=0)
        self.body.grid_rowconfigure(1, weight=1)
        self._heading("INFORMAÇÕES", "Sobre o projeto", "Um sistema acadêmico completo com interface gráfica.")
        panel = ctk.CTkFrame(self.body, fg_color=WHITE, corner_radius=17, border_width=1, border_color=LINE)
        panel.grid(row=1, column=0, sticky="nsew")
        sections = [
            ("O que o sistema faz", "Permite cadastrar, consultar, editar e excluir alunos. Os registros são mantidos na nuvem por meio do MongoDB Atlas."),
            ("Como pesquisar", "Na aba Alunos, pesquise por nome ou matrícula e combine filtros de curso e situação acadêmica. Os resultados são paginados."),
            ("Tecnologias utilizadas", "Python, CustomTkinter, PyMongo, python-dotenv e MongoDB Atlas."),
            ("Onde ficam os dados", "Banco: sistema_academico (configurável no .env)  •  Coleção: alunos."),
        ]
        for idx, (title, description) in enumerate(sections):
            section = ctk.CTkFrame(panel, fg_color="#F7FAFD", corner_radius=12)
            section.pack(fill="x", padx=23, pady=(22 if idx == 0 else 0, 12))
            label(section, title, 16, "bold", NAVY).pack(anchor="w", padx=18, pady=(14, 4))
            label(section, description, 12, color=MUTED, wraplength=680, justify="left").pack(anchor="w", padx=18, pady=(0, 16))

    def open_new(self):
        if self.repository:
            StudentForm(self)

    def open_edit(self, student):
        if self.repository:
            StudentForm(self, student)

    def save_student(self, old, data, dialog):
        def task():
            if old:
                return self.repository.update(str(old["_id"]), data)
            return self.repository.create(data)

        def success(result):
            if old and result is False:
                dialog.recover()
                self.bottom_status.configure(text="Este aluno não foi encontrado no banco. Atualize a listagem.", text_color=RED)
                return
            if dialog.winfo_exists():
                dialog.destroy()
            self.bottom_status.configure(text="Aluno atualizado com sucesso." if old else "Aluno cadastrado com sucesso.", text_color=GREEN)
            self.navigate(self.page)

        def failed(exc):
            if isinstance(exc, DuplicateKeyError):
                dialog.recover("Esta matrícula já está cadastrada. Utilize outro número.")
            else:
                dialog.recover("Não foi possível salvar. Confira a conexão e tente novamente.")

        self.run_job(task, success, failed)

    def delete_student(self, old, dialog):
        def success(deleted):
            if not deleted:
                dialog.recover()
                self.bottom_status.configure(text="O registro já não existe. Atualize o cadastro.", text_color=RED)
                return
            if dialog.winfo_exists():
                dialog.destroy()
            self.bottom_status.configure(text="Aluno excluído com sucesso.", text_color=GREEN)
            self.navigate(self.page)

        self.run_job(lambda: self.repository.delete(str(old["_id"])), success, lambda _exc: dialog.recover())

    def on_close(self):
        self.executor.shutdown(wait=False, cancel_futures=True)
        if self.client:
            self.client.close()
        self.destroy()


if __name__ == "__main__":
    app = AcademicoApp()
    app.mainloop()
