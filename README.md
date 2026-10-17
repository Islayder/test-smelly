# Laboratório de Test Smells — Gerenciador de Usuários

Projeto acadêmico de Teste de Software da PUC Minas. O serviço e a suíte
original foram preservados; a suíte refatorada separa cenários, aplica AAA
e verifica comportamentos públicos.

## Trabalho – Refatoração de Testes e Test Smells

**Aluno:** Islayder Jackson Ribeiro de Oliveira — **matrícula:** 859552.

Ambiente validado: Node.js 24.19.0 e npm 11.17.0.

No PowerShell com scripts desabilitados, use `npm.cmd` e `npx.cmd` nos
comandos abaixo, sem alterar a política de execução do Windows.

```sh
npm install
npm test
npx eslint __tests__/userService.clean.test.js
npx eslint .
```

- Suíte limpa: `__tests__/userService.clean.test.js`.
- Suíte original preservada: `test/userService.smelly.test.js`.
- [Relatório final em PDF](docs/Relatorio_Test_Smells.pdf).
- [Fonte do relatório](docs/Relatorio_Test_Smells.md).
- [Evidência visual do ESLint](docs/eslint-inicial.png).
- [Resultados e comandos de validação](docs/VALIDACAO.md).

São 21 testes aprovados e 1 skip pertencente ao original. O lint do clean
retorna zero erros e avisos. O lint completo retorna 4 erros e 2 avisos
exclusivamente no original, preservado para comparação. ESLint 8.57.1 foi
fixado para utilizar o formato `.eslintrc.json` exigido no trabalho.

Para medir somente a cobertura da suíte limpa:

```sh
npm run coverage -- --runInBand --runTestsByPath __tests__/userService.clean.test.js --coverageReporters=text --coverageReporters=json-summary
```

Para regenerar o PDF e a reprodução visual do log em Windows com Python 3:

```sh
python -m pip install reportlab
python docs/gerar_relatorio.py
```

A imagem representa fielmente o log registrado; não é uma captura histórica
da primeira execução. [Fork de entrega](https://github.com/Islayder/test-smelly).
