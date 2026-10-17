# Validação da refatoração

Data: 17/10/2026. Base:
[`CleitonSilvaT/test-smelly`, commit fc5cc1206e9bcd40d5b6c705d48a67659672c6c5](https://github.com/CleitonSilvaT/test-smelly/commit/fc5cc1206e9bcd40d5b6c705d48a67659672c6c5).
Fork de entrega: https://github.com/Islayder/test-smelly.

## Ambiente e instalação

| Ferramenta | Versão |
| --- | --- |
| Node.js | v24.19.0 |
| npm | 11.17.0 |
| Jest / babel-jest | 29.7.0 |
| ESLint | 8.57.1 |
| eslint-plugin-jest | 29.17.0 |

A instalação final foi executada com `npm install`, código de saída 0:
dependências atualizadas, 440 pacotes auditados. O lockfile está incluído e
suas dependências raiz coincidem com `package.json`. A instalação informou
33 vulnerabilidades em dependências (5 moderadas e 28 altas); atualizações
automáticas que mudassem o conjunto de ferramentas ficaram fora do escopo.

Para reproduzir:

```sh
npm install
npm test
npx eslint __tests__/userService.clean.test.js
npx eslint .
npm run coverage -- --runInBand --runTestsByPath __tests__/userService.clean.test.js --coverageReporters=text --coverageReporters=json-summary
```

## Resultados reais

| Execução | Resultado | Código |
| --- | --- | --- |
| `npm test` antes da refatoração | 1 suíte aprovada; 4 testes aprovados; 1 skip; zero falhas | 0 |
| Primeiro diagnóstico compatível do ESLint | 4 erros e 2 avisos no original | 1 |
| `npm test` final | 2 suítes aprovadas; 21 testes aprovados; 1 skip; zero falhas | 0 |
| ESLint no clean | 0 erros, 0 avisos e saída vazia | 0 |
| ESLint completo | 4 erros e 2 avisos exclusivamente no original | 1 |
| Coverage somente clean | 17 testes aprovados; nenhuma falha | 0 |

O único skip permanece em `test/userService.smelly.test.js`, linha 77,
porque esse arquivo deve permanecer intacto. Seu cenário equivalente foi
implementado e é executado na suíte limpa. O Jest descobre ambas as pastas;
nenhum teste ou arquivo foi excluído para facilitar a validação.

Saídas completas preservadas:

- `npm-test-inicial.txt` e `npm-test-final.txt`.
- `eslint-inicial.txt`, `eslint-clean-final.txt` e `eslint-final.txt`.
- `cobertura-inicial.txt` e `cobertura-clean.txt`.

O arquivo de lint clean está vazio porque o comando terminou sem mensagens.
O lint também foi conferido pelo formato JSON: contadores zero no clean e
no serviço; somente o original possui diagnósticos, sem mensagens suprimidas.

## ESLint e evidência visual

A configuração mantém os ambientes es2021, node e jest/globals, os presets
eslint:recommended e plugin:jest/recommended, ecmaVersion latest,
sourceType module e plugin jest. As severidades exigidas são:

| Regra | Severidade | Ocorrências no original |
| --- | --- | --- |
| jest/no-disabled-tests | warn | 1, linha 77 |
| jest/no-conditional-expect | error | 4, linhas 44, 46, 49 e 73 |
| jest/no-identical-title | error | 0 |
| jest/expect-expect, do preset | warn | 1, linha 77 |

A instalação sem versão trouxe ESLint 10.13.0; a primeira tentativa de
`npx eslint .` terminou com código 2, exigindo eslint.config.*. A saída está
em `eslint-primeira-tentativa.txt`. Fixou-se ESLint 8.57.1, compatível com o
plugin instalado, para consumir exatamente `.eslintrc.json`, sem desligar
regras. Essa adaptação foi autorizada no pedido da atividade.

O ESLint foi executado sobre a suíte original com:

```sh
npx.cmd eslint test/userService.smelly.test.js
```

No PowerShell, `npx.cmd` executa a mesma ferramenta sem carregar `npx.ps1`;
nenhuma política de execução do Windows foi alterada. A coleta e as
validações também podem usar `npm.cmd`, pelo mesmo motivo.

`eslint-inicial.txt` registra o diagnóstico, com posições, mensagens, regras
e totais. A Figura 1, em `eslint-inicial.png`, apresenta o resultado dessa
execução e está incluída na seção 3 do relatório: quatro erros de
jest/no-conditional-expect e dois avisos das regras jest/no-disabled-tests
e jest/expect-expect.

## Smells confirmados

| Smell | Evidência original | Risco | Correção |
| --- | --- | --- | --- |
| Eager Test | L18–30: criação e busca verificadas no mesmo teste | Responsabilidades misturadas e diagnóstico prejudicado | Casos distintos para criar e buscar; cadastro apenas no Arrange da busca |
| Conditional Logic in Test | L40–49: for/if; L70–73: expect somente no catch | Expectativas dependentes do fluxo e falso positivo sem exceção | Casos determinísticos de comum/admin e matcher toThrow |
| Fragile Test | L61–63: linha e cabeçalho com decoração exata | Falhas por mudanças cosméticas | Verificar título inicial, ID, nome e status sem fixar layout |

Disabled Test (teste ignorado, L77–79) é um achado adicional, sem substituir
os três smells obrigatórios. O caso vazio agora verifica a mensagem real do
relatório; a API retorna texto, não uma lista.

## Preservação semântica

| Original | Comportamento preservado no clean |
| --- | --- |
| Criar e buscar | ID não vazio; dados informados; usuário ativo; consulta por ID com nome e status |
| Desativar usuários não administradores | Comum: true e cadastro inativo consultável; admin: false e status ativo |
| Gerar relatório formatado | Título inicial, ID, nome e status; ambos os usuários incluídos sem layout exato |
| Rejeitar menor de idade | Exceção aos 17 anos com mensagem exata; falha obrigatória quando não há exceção |
| Caso vazio ignorado | Mensagem “Nenhum usuário cadastrado.” em teste executável |

Os 17 testes incluem ainda os campos obrigatórios, o limite de 18 anos,
criação explícita de administrador, IDs inexistentes e relatório de usuário
inativo. Cada caso tem Arrange, Act e Assert explícitos, sem condicionais,
laços, skips, todos, mocks artificiais ou helpers genéricos. Os hooks só
instanciam o serviço e isolam o banco compartilhado por `_clearDB()`.

Nos casos de exceção, o Act define a chamada adiada, executada pelo matcher
no Assert. `toThrow(new Error(...))` verifica mensagem exata no Jest 29.7.0;
uma string isolada aceitaria correspondência parcial. Criação e busca usam
`toMatchObject` para verificar campos relevantes sem impedir campos futuros.
Os status são comparados como palavras completas: inativo não satisfaz ativo.

## Cobertura medida

| Suíte sobre src/userService.js | Instruções | Ramos | Funções | Linhas |
| --- | --- | --- | --- | --- |
| Original, antes da refatoração | 85,71% | 75% | 100% | 85,71% |
| Somente clean, execução final | 100% | 100% | 100% | 100% |

As medições foram executadas, não inferidas. A segunda execução selecionou
apenas `__tests__/userService.clean.test.js`, evitando atribuir ao clean a
cobertura do original. Cobertura complementa a matriz funcional; não prova
ausência de defeitos.

## Integridade e arquivos principais

Os hashes SHA-256 abaixo coincidem com os obtidos no checkout inicial:

```text
test/userService.smelly.test.js
2B3FACB4D424F2D4604E680BAB725FC39B34460A58C29003C6A2FE3ECA02E48A

src/userService.js
C3121F0AD76F2F5C082AC50AFFC6736995C00D07593C72F4F16C876BAF3663C8
```

A comparação com o commit-base também confirmou conteúdo idêntico,
normalizando apenas CRLF/LF para considerar o checkout Windows. O diff dos
dois arquivos é vazio. Nenhuma regra de produção foi alterada. O caminho
real do original é `test/`, embora o enunciado cite `__tests__/`; ele foi
mantido no local real e o clean foi criado no caminho solicitado.

As alterações abrangem dependências e lockfile, `.eslintrc.json`,
`.gitignore`, README, suíte limpa e documentação em `docs/`. `.gitattributes`
declara PDF e PNG como binários para preservar seus bytes no Git. O relatório
final tem **4 páginas: 1 capa e 3 de conteúdo**, com nome e matrícula
conferidos. Todas as páginas foram inspecionadas, incluindo a legibilidade
da Figura 1. O script `gerar_relatorio.py` permite atualizar o relatório PDF.

Arquivos temporários, prévias, caches e documentos internos de revisão não
integram a entrega. node_modules e coverage são ignorados pelo Git. Não há
supressões de lint, caminhos pessoais ou credenciais nos artefatos publicados.
