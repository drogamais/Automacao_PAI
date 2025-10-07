# Automação de Relatórios PAI

Este projeto consiste em uma aplicação de desktop desenvolvida em Python para automatizar o download e processamento de relatórios financeiros e de performance do sistema PAI da Febrafar. A aplicação possui uma interface gráfica para facilitar a interação do usuário.

## ✨ Funcionalidades

-   **Automação Completa:** Baixa todos os relatórios (Financeiro e Performance) para uma ou mais lojas em um período especificado e processa os dados, inserindo-os no banco de dados.
-   **Evolução Mensal:** Baixa especificamente os relatórios de evolução mensal e os processa.
-   **Busca de Lojas:** Permite buscar todas as lojas que tiveram lançamentos em um determinado ano, exibindo a quantidade de meses com dados.
-   **Execução em Lote:** Permite selecionar múltiplas lojas a partir da busca e executar a automação completa para todas elas de uma só vez.
-   **Interface Gráfica:** Interface amigável construída com `ttkbootstrap` para uma experiência de usuário moderna.

## 🚀 Começando

Siga estas instruções para configurar e executar o projeto em seu ambiente de desenvolvimento.

### Pré-requisitos

-   [Python](https://www.python.org/downloads/) (versão 3.10 ou superior)
-   [Git](https://git-scm.com/downloads/)

### 1. Clonando o Repositório

Primeiro, clone o repositório para a sua máquina local usando o seguinte comando no terminal:

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd Automacao_PAI
```

2. Configurando o Ambiente Virtual

É uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
# No Windows:
.\venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
```

3. Instalando as Dependências

Com o ambiente virtual ativado, instale todas as bibliotecas necessárias com um único comando:

```bash
pip install -r requirements.txt
```

4. Configurando as Credenciais

Para que a aplicação funcione, é necessário fornecer as credenciais de acesso ao sistema PAI e ao banco de dados.

    Encontre o arquivo config.json.example na raiz do projeto. Ele serve como um modelo.

    Crie uma cópia deste arquivo na mesma pasta e renomeie-a para config.json.

    Abra o config.json e preencha com suas credenciais reais. O arquivo deve ficar assim:

```json
{
  "login": {
    "usuario": "seu_email@dominio.com",
    "senha": "sua_senha_do_pai"
  },
  "database": {
    "user": "seu_usuario_do_banco",
    "password": "sua_senha_do_banco",
    "host": "ip_do_banco",
    "port": 3306,
    "database": "nome_do_banco"
  }
}
```

▶️ Como Executar

Com o ambiente virtual ativado e as credenciais configuradas, execute o seguinte comando na raiz do projeto para iniciar a aplicação:

```bash
python main.py
```

📦 Gerando um Executável (Opcional)

Você pode compilar a aplicação em um único executável (.exe) para facilitar a distribuição, sem a necessidade de ter o Python instalado na máquina de destino.

    Ícone: Certifique-se de que o ícone icone.ico está dentro da pasta assets/.

    Execute o PyInstaller: No terminal (com o ambiente virtual ativado), execute o comando:

    ```bash
        pyinstaller --name "Automacao PAI" --windowed --icon="assets/icone.ico" main.py
    ```

    Encontre o Executável: Após a compilação, uma nova pasta dist será criada. Dentro dela, você encontrará a pasta Automacao PAI. O seu programa pronto para uso é o Automacao PAI.exe que está dentro desta pasta. Para compartilhar, basta compactar a pasta Automacao PAI inteira e enviá-la.

📂 Estrutura do Projeto
```bash
    ├── assets/             # Recursos estáticos, como o ícone da aplicação.
    ├── controller/         # Orquestra a lógica da aplicação (workflows).
    ├── processing/         # Módulos para processar os dados dos arquivos Excel.
    ├── scraping/           # Módulos para automação web com Selenium.
    ├── utils/              # Funções de utilidade (conexão com DB, config, etc.).
    ├── view/               # Módulos da interface gráfica (GUI).
    ├── config.json.example # Arquivo de exemplo para as credenciais.
    ├── main.py             # Ponto de entrada da aplicação.
    └── requirements.txt    # Lista de dependências Python.
```