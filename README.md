# 🎓 Aurora | Sistema Acadêmico

**Sistema de gestão de alunos desenvolvido em Python, com interface gráfica e integração ao MongoDB Atlas.**

`Python 3.11+` · `CustomTkinter` · `PyMongo` · `MongoDB Atlas`

O projeto foi criado para o desafio prático de **CRUD com Python e MongoDB**. Ele permite organizar informações acadêmicas, realizar as quatro operações básicas de cadastro e pesquisar registros usando filtros combinados.

---

## 🖥️ Visão geral

A tela inicial apresenta a situação dos cadastros, com indicadores de **total de alunos, matriculados, concluintes e cursos**. A interface utiliza azul-marinho, azul-claro, acqua e branco.

![Painel geral do Sistema Acadêmico Aurora](imagens/01-painel-geral.png)

## ✅ Funcionalidades

| Funcionalidade | Como funciona |
| --- | --- |
| **Cadastrar** | Registra nome, matrícula, e-mail, curso, período, situação e observações. |
| **Consultar** | Lista os alunos armazenados no Atlas, com paginação. |
| **Atualizar** | Permite editar as informações de um aluno existente. |
| **Excluir** | Remove um registro após confirmação. |
| **Filtrar** | Pesquisa por nome ou matrícula, curso e situação acadêmica, inclusive combinando critérios. |

A matrícula é tratada como identificador único do aluno, evitando cadastros com a mesma matrícula.

## 📚 Cadastro e consulta

O formulário permite registrar alunos e atualizar os dados diretamente no banco. A listagem apresenta as principais informações e botões para editar ou excluir.

**Tela de cadastro**

![Formulário de cadastro de aluno](imagens/06-cadastro-aluno.png)

**Lista de alunos**

![Listagem de alunos no sistema](imagens/02-listagem-alunos.png)

## 🔎 Consultas com filtros

Os filtros são executados na consulta ao MongoDB, e não apenas na exibição da tela. É possível buscar por **nome ou matrícula**, selecionar um **curso** e restringir a **situação acadêmica** (Matriculado, Trancado ou Concluído).

**Filtragem por curso**

![Consulta filtrada pelo curso Ciência da Computação](imagens/03-filtro-curso.png)

**Filtragem por situação acadêmica**

![Consulta filtrada pela situação Matriculado](imagens/04-filtro-situacao.png)

**Busca por nome combinada com situação**

![Consulta por nome Maria e situação Matriculado](imagens/05-busca-nome.png)

## ✏️ Atualização e exclusão

Na listagem, o botão **Editar** abre o formulário com os dados existentes. Já o botão **Excluir** solicita uma confirmação antes de remover o aluno.

**Edição de aluno**

![Formulário para editar os dados de um aluno](imagens/07-edicao-aluno.png)

**Confirmação de exclusão**

![Janela de confirmação antes de excluir um aluno](imagens/08-confirmacao-exclusao.png)

## ☁️ Integração com MongoDB Atlas

O Python utiliza **PyMongo** para gravar e consultar documentos na nuvem. O banco é `sistema_academico` e a coleção utilizada é `alunos`. Cada documento representa um aluno, sem precisar criar tabelas SQL.

![Coleção alunos visualizada no MongoDB Atlas](imagens/09-mongodb-atlas.png)

As capturas foram feitas em momentos diferentes dos testes; por isso, a quantidade de alunos exibida pode variar entre as telas.

## 🛠️ Como executar

**1.** Instale o Python 3.11 ou superior e abra a pasta do projeto no VS Code.

**2.** No terminal, instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

**3.** Crie um arquivo `.env` com base no `.env.example` e configure sua própria conexão com o MongoDB Atlas:

```dotenv
MONGO_URI=mongodb+srv://USUARIO:SENHA@SEU_CLUSTER.mongodb.net/
MONGO_DB=sistema_academico
```

**4.** Teste a conexão e inicie a aplicação:

```powershell
python verificar_conexao.py
python main.py
```

Para executar os testes de lógica:

```powershell
python testes.py
```

> **Segurança:** o arquivo `.env` contém credenciais e não deve ser enviado ao GitHub. O repositório deve incluir apenas o `.env.example`, com valores de exemplo. Utilize dados fictícios nas demonstrações.

## 📁 Arquivos principais

- `main.py` — interface, validação, operações CRUD e filtros.
- `verificar_conexao.py` — verificação de acesso ao Atlas.
- `testes.py` — testes de lógica.
- `requirements.txt` — bibliotecas necessárias.
- `.env.example` — modelo das configurações de conexão.
- `imagens/` — capturas de tela usadas neste README.

---

**Resultado:** uma aplicação desktop funcional para gerenciamento acadêmico, com operações CRUD, consultas filtradas e persistência de dados no MongoDB Atlas.
