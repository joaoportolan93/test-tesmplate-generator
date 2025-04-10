# Gerador de Relatórios de Teste

Uma aplicação web para criar e gerenciar relatórios de teste de software de forma profissional e elegante.

## Características

- Interface intuitiva para criação e edição de testes
- Suporte a steps detalhados com status
- Informações do ambiente de teste
- Campos personalizados
- Relatório visual com gráficos e estatísticas
- Exportação em HTML
- Design responsivo e moderno

## Requisitos

- Python 3.7+
- SQLite3

## Instalação

1. Clone o repositório:
```bash
git clone [url-do-repositorio]
cd [nome-do-diretorio]
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Inicie o servidor:
```bash
python app.py
```

2. Acesse a aplicação em seu navegador:
```
http://localhost:5000
```

## Estrutura do Projeto

```
.
├── app.py              # Aplicação Flask principal
├── requirements.txt    # Dependências Python
├── tests.db           # Banco de dados SQLite
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/
    ├── index.html     # Página principal
    └── report.html    # Template do relatório
```

## Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 