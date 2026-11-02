# 🎓 Aurora | Sistema Acadêmico

**Gestão de alunos em uma aplicação desktop simples de usar, com dados armazenados na nuvem.**

`Python 3.11+` · `CustomTkinter` · `PyMongo` · `MongoDB Atlas`

O **Aurora** foi desenvolvido para o desafio prático de **CRUD com Python e MongoDB**. A proposta foi criar algo que fosse além de operações no terminal: um sistema com interface gráfica, no qual é possível cadastrar alunos, acompanhar suas situações acadêmicas e localizar informações com facilidade.

Todas as operações são feitas pela aplicação em Python, enquanto o **MongoDB Atlas** mantém os registros armazenados. Assim, o projeto reúne interface, lógica de programação e banco de dados em uma solução funcional.

---

## 🖥️ Um panorama da instituição

Ao abrir o sistema, o usuário encontra um painel com informações gerais dos cadastros: **total de alunos, matriculados, concluintes e quantidade de cursos**. Esses indicadores ajudam a visualizar rapidamente a situação acadêmica registrada no banco.

![Painel geral do Sistema Acadêmico Aurora](https://github.com/user-attachments/assets/e13c272f-c441-4118-a0a7-ec29e0363c9d)

## 📚 Cadastro e gerenciamento de alunos

O Aurora concentra as quatro operações de um CRUD em uma única interface:

| Operação | O que é possível fazer |
| --- | --- |
| **Cadastrar** | Adicionar um aluno com nome, matrícula, e-mail, curso, período, situação acadêmica e observações. |
| **Consultar** | Visualizar os alunos cadastrados, com listagem organizada e paginação. |
| **Atualizar** | Abrir um registro existente, modificar seus dados e salvar as alterações. |
| **Excluir** | Remover um aluno após confirmar a ação. |

O cadastro possui validação dos campos e verifica a matrícula para evitar registros duplicados. Os dados não ficam apenas na tela: são enviados ao banco de dados.

### Formulário de cadastro

O formulário reúne as informações necessárias para registrar um aluno e permite selecionar sua situação como **Matriculado, Trancado ou Concluído**.

![Formulário de cadastro de aluno](https://github.com/user-attachments/assets/99688e78-5509-47b1-b786-c27f580dd4a7)

### Listagem dos alunos

Na área **Alunos**, cada registro aparece com seus dados principais e ações de edição e exclusão. A listagem é paginada para facilitar a navegação.

![Listagem de alunos no sistema](https://github.com/user-attachments/assets/aac8de05-315e-4221-99a0-8789bdcea58b)

## 🔎 Consultas com filtros

Um dos pontos centrais do projeto é a possibilidade de **consultar dados de maneiras diferentes**, sem precisar percorrer todos os cadastros manualmente.

A pesquisa permite combinar:

- **Nome ou matrícula:** encontra um aluno específico, inclusive pela parte inicial do nome.
- **Curso:** exibe apenas os alunos de determinada formação.
- **Situação acadêmica:** separa matriculados, trancados e concluintes.

Os critérios são usados nas consultas feitas ao **MongoDB Atlas por meio do PyMongo**. Por exemplo, é possível procurar por “Maria” e, ao mesmo tempo, mostrar somente os registros com situação **Matriculado**.

### Filtro por curso

Neste exemplo, a listagem apresenta apenas alunos de **Ciência da Computação**.

![Consulta filtrada pelo curso Ciência da Computação](https://github.com/user-attachments/assets/632f9768-1e03-44af-a0da-096d20784352)

### Filtro por situação acadêmica

Aqui são exibidos somente os alunos com a situação **Matriculado**.

![Consulta filtrada pela situação Matriculado](https://github.com/user-attachments/assets/118f6088-f672-4839-9664-e0710b13cec9)

### Busca combinada

A aplicação também permite usar mais de um critério na mesma pesquisa, como **nome + situação acadêmica**.

![Consulta por nome Maria e situação Matriculado](https://github.com/user-attachments/assets/53ca2634-28a0-405d-8d18-29261f30fcd0)

## ✏️ Edição e exclusão com confirmação

Para atualizar um cadastro, basta clicar em **Editar**. O formulário abre com as informações existentes, que podem ser alteradas e salvas no Atlas.

![Formulário para editar os dados de um aluno](https://github.com/user-attachments/assets/bbf34f82-8a09-4d15-bf32-76a03eda86e1)

Já a exclusão exige uma **confirmação antes da remoção**, evitando que um registro seja apagado por engano.

![Janela de confirmação antes de excluir um aluno](https://github.com/user-attachments/assets/5dbfab42-c787-4e9e-9ae8-1b4599165b37)

## ☁️ Como o MongoDB entra no projeto

A interface foi construída em **CustomTkinter**, e o Python utiliza o **PyMongo** para se comunicar com o MongoDB Atlas. Quando um aluno é cadastrado, atualizado ou excluído, a operação é realizada no banco de dados.

```text
Interface Aurora → Python + PyMongo → MongoDB Atlas
```

Os registros ficam organizados desta forma:

- **Banco de dados:** `sistema_academico`
- **Coleção:** `alunos`
- **Cada documento:** informações de um aluno, identificadas por um `_id` do MongoDB.

Por ser um banco **NoSQL**, o MongoDB trabalha com coleções e documentos, sem exigir a criação de tabelas SQL.

![Coleção alunos visualizada no MongoDB Atlas](https://github.com/user-attachments/assets/f8217588-2e85-4b41-ac52-17a834a8e762)

## 🛠️ Tecnologias utilizadas

| Tecnologia | Utilização |
| --- | --- |
| **Python** | Regras do sistema, validação e operações CRUD. |
| **CustomTkinter** | Telas, botões, formulários e painel de indicadores. |
| **PyMongo** | Comunicação com o MongoDB e execução das consultas com filtros. |
| **MongoDB Atlas** | Armazenamento dos registros na nuvem. |
| **python-dotenv** | Leitura das configurações de conexão no arquivo `.env`. |

## 🚀 Como executar no computador

**1.** Instale o **Python 3.11 ou superior** e abra a pasta do projeto no VS Code.

**2.** No terminal, instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

**3.** Crie um arquivo chamado `.env` a partir do `.env.example` e coloque a string de conexão do seu próprio cluster no MongoDB Atlas:

```dotenv
MONGO_URI=mongodb+srv://USUARIO:SENHA@SEU_CLUSTER.mongodb.net/
MONGO_DB=sistema_academico
```

**4.** Verifique a conexão:

```powershell
python verificar_conexao.py
```

**5.** Inicie a interface:

```powershell
python main.py
```

Para executar os testes de lógica:

```powershell
python testes.py
```

> 🔐 **Segurança:** o arquivo `.env` contém credenciais reais e **não deve ser publicado no GitHub**. O repositório deve manter apenas o `.env.example`, com dados de exemplo. As demonstrações devem utilizar informações fictícias.

## 📁 Organização dos arquivos

```text
sistema_academico/
├── main.py                 # Interface, CRUD, validações e filtros
├── verificar_conexao.py    # Teste de conexão com o Atlas
├── testes.py               # Testes de lógica
├── requirements.txt        # Dependências do projeto
├── .env.example            # Exemplo de configuração
├── .gitignore              # Arquivos que não devem ir para o GitHub
└── README.md               # Documentação do projeto
```

---

### ✅ Resultado do desafio

O Aurora reúne os requisitos solicitados na atividade: **cadastrar, consultar, atualizar e excluir registros (CRUD)**, além de **realizar consultas com filtros**. Como complemento, o sistema conta com **interface gráfica**, painel de indicadores, validação de cadastros e armazenamento no **MongoDB Atlas**.

**Uma aplicação acadêmica que permite demonstrar, na prática, a integração entre Python, interface e banco de dados NoSQL.**
