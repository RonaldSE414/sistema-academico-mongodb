from main import connect_database


def main():
    client = None
    try:
        client, repository = connect_database()
        print("Conexão com o MongoDB Atlas realizada com sucesso.")
        print(f"Coleção: {repository.collection.full_name}")
        print(f"Alunos cadastrados: {repository.stats()['total']}")
    except Exception as error:
        print("Não foi possível conectar ao MongoDB Atlas.")
        print(f"Tipo do erro: {error.__class__.__name__}")
        print("Confira o .env, a senha, o usuário e o IP liberado no Atlas.")
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
