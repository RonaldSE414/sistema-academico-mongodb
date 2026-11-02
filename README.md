# 🎓 Aurora | Sistema Acadêmico

**Sistema de gestão de alunos desenvolvido em Python, com interface gráfica e integração ao MongoDB Atlas.**

`Python 3.11+` · `CustomTkinter` · `PyMongo` · `MongoDB Atlas`

O projeto foi criado para o desafio prático de **CRUD com Python e MongoDB**. Ele permite organizar informações acadêmicas, realizar as quatro operações básicas de cadastro e pesquisar registros usando filtros combinados.

---

## 🖥️ Visão geral

A tela inicial apresenta a situação dos cadastros, com indicadores de **total de alunos, matriculados, concluintes e cursos**. A interface utiliza azul-marinho, azul-claro, acqua e branco.

![Painel geral do Sistema Acadêmico Aurora]<img width="1920" height="1020" alt="Captura de tela 2026-11-02 042134" src="https://github.com/user-attachments/assets/e13c272f-c441-4118-a0a7-ec29e0363c9d" />


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

![Formulário de cadastro de aluno]<img width="1917" height="1020" alt="Captura de tela 2026-11-02 042731" src="https://github.com/user-attachments/assets/99688e78-5509-47b1-b786-c27f580dd4a7" />


**Lista de alunos**

![Listagem de alunos no sistema]<img width="1920" height="1020" alt="Captura de tela 2026-11-02 042329" src="https://github.com/user-attachments/assets/aac8de05-315e-4221-99a0-8789bdcea58b" />


## 🔎 Consultas com filtros

Os filtros são executados na consulta ao MongoDB, e não apenas na exibição da tela. É possível buscar por **nome ou matrícula**, selecionar um **curso** e restringir a **situação acadêmica** (Matriculado, Trancado ou Concluído).

**Filtragem por curso**

![Consulta filtrada pelo curso Ciência da Computação]<img width="1920" height="1020" alt="Captura de tela 2026-11-02 042409" src="https://github.com/user-attachments/assets/632f9768-1e03-44af-a0da-096d20784352" />


**Filtragem por situação acadêmica**

![Consulta filtrada pela situação Matriculado]<img width="1920" height="1020" alt="Captura de tela 2026-11-02 042439" src="https://github.com/user-attachments/assets/118f6088-f672-4839-9664-e0710b13cec9" />


**Busca por nome combinada com situação**

![Consulta por nome Maria e situação Matriculado]<img width="1920" height="1020" alt="Captura de tela 2026-11-02 042507" src="https://github.com/user-attachments/assets/53ca2634-28a0-405d-8d18-29261f30fcd0" />


## ✏️ Atualização e exclusão

Na listagem, o botão **Editar** abre o formulário com os dados existentes. Já o botão **Excluir** solicita uma confirmação antes de remover o aluno.

**Edição de aluno**

![Formulário para editar os dados de um aluno]<img width="1917" height="1015" alt="Captura de tela 2026-11-02 042808" src="https://github.com/user-attachments/assets/bbf34f82-8a09-4d15-bf32-76a03eda86e1" />


**Confirmação de exclusão**

![Janela de confirmação antes de excluir um aluno]<img width="1917" height="1015" alt="Captura de tela 2026-11-02 042841" src="https://github.com/user-attachments/assets/5dbfab42-c787-4e9e-9ae8-1b4599165b37" />


## ☁️ Integração com MongoDB Atlas

O Python utiliza **PyMongo** para gravar e consultar documentos na nuvem. O banco é `sistema_academico` e a coleção utilizada é `alunos`. Cada documento representa um aluno, sem precisar criar tabelas SQL.

![Coleção alunos visualizada no MongoDB Atlas]<img width="1917" height="720" alt="Captura de tela 2026-11-02 042934" src="https://github.com/user-attachments/assets/f8217588-2e85-4b41-ac52-17a834a8e762" />



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
