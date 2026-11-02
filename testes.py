import unittest
from unittest.mock import MagicMock

from bson import ObjectId

from main import COURSES, StudentRepository, validate_student


class ValidacaoAlunoTests(unittest.TestCase):
    def setUp(self):
        self.aluno = {
            "nome": "Mariana Lima",
            "matricula": "20260001",
            "email": "mariana@exemplo.com",
            "curso": "Pedagogia",
            "periodo": "3",
            "situacao": "Matriculado",
            "observacoes": "Turma da manhã",
        }

    def test_cadastro_valido(self):
        dados = validate_student(self.aluno)
        self.assertEqual(dados["periodo"], 3)
        self.assertEqual(dados["matricula"], "20260001")

    def test_matricula_com_letras_maiusculas(self):
        dados = validate_student({**self.aluno, "matricula": "abc-1234"})
        self.assertEqual(dados["matricula"], "ABC-1234")

    def test_nome_obrigatorio(self):
        with self.assertRaises(ValueError):
            validate_student({**self.aluno, "nome": ""})

    def test_periodo_invalido(self):
        with self.assertRaises(ValueError):
            validate_student({**self.aluno, "periodo": "13"})

    def test_email_invalido(self):
        with self.assertRaises(ValueError):
            validate_student({**self.aluno, "email": "endereco_sem_arroba"})

    def test_situacao_invalida(self):
        with self.assertRaises(ValueError):
            validate_student({**self.aluno, "situacao": "Desconhecida"})


class RepositorioTests(unittest.TestCase):
    def setUp(self):
        self.collection = MagicMock()
        self.repo = StudentRepository(self.collection)
        self.aluno = {
            "nome": "Mariana Lima", "matricula": "20260001", "email": "",
            "curso": "Pedagogia", "periodo": 3, "situacao": "Matriculado", "observacoes": "",
        }

    def test_criar_aluno(self):
        ident = ObjectId()
        self.collection.insert_one.return_value.inserted_id = ident
        self.assertEqual(self.repo.create(self.aluno), str(ident))
        self.assertEqual(self.collection.insert_one.call_args.args[0]["matricula"], "20260001")

    def test_consultar_aluno(self):
        ident = ObjectId()
        self.collection.find_one.return_value = self.aluno
        self.assertEqual(self.repo.get(str(ident)), self.aluno)
        self.collection.find_one.assert_called_once_with({"_id": ident})

    def test_atualizar_aluno(self):
        self.collection.update_one.return_value.matched_count = 1
        self.assertTrue(self.repo.update(str(ObjectId()), {**self.aluno, "periodo": 4}))
        self.assertEqual(self.collection.update_one.call_args.args[1]["$set"]["periodo"], 4)

    def test_excluir_aluno(self):
        self.collection.delete_one.return_value.deleted_count = 1
        self.assertTrue(self.repo.delete(str(ObjectId())))

    def test_consulta_com_filtros_combinados(self):
        filtro = self.repo.build_query("mariana", "Pedagogia", "Matriculado")
        self.assertEqual(filtro["curso"], "Pedagogia")
        self.assertEqual(filtro["situacao"], "Matriculado")
        self.assertEqual(len(filtro["$or"]), 2)

    def test_busca_trata_caracteres_especiais(self):
        filtro = self.repo.build_query("A+B", "Todos os cursos", "Todas as situações")
        self.assertEqual(filtro["$or"][0]["nome"]["$regex"], "A\\+B")

    def test_paginacao(self):
        self.collection.count_documents.return_value = 30
        estudantes, total = self.repo.list_students(page=1, per_page=10)
        self.assertEqual(total, 30)
        self.collection.find.return_value.sort.return_value.skip.assert_called_once_with(10)
        self.collection.find.return_value.sort.return_value.skip.return_value.limit.assert_called_once_with(10)

    def test_cursos_disponiveis(self):
        self.assertIn("Pedagogia", COURSES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
