const { UserService } = require('../src/userService');

describe('UserService - comportamentos públicos', () => {
  let userService;

  beforeEach(() => {
    userService = new UserService();
    userService._clearDB();
  });

  afterEach(() => {
    userService._clearDB();
  });

  describe('createUser', () => {
    test('cria um usuário comum ativo com os dados informados', () => {
      // Arrange
      const nome = 'Alice';
      const email = 'alice@email.com';
      const idade = 28;

      // Act
      const usuario = userService.createUser(nome, email, idade);

      // Assert
      expect(usuario).toMatchObject({
        id: expect.any(String),
        nome,
        email,
        idade,
        isAdmin: false,
        createdAt: expect.any(Date),
        status: 'ativo',
      });
      expect(usuario.id).not.toBe('');
    });

    test('cria um administrador quando solicitado', () => {
      // Arrange
      const nome = 'Admin';
      const email = 'admin@email.com';
      const idade = 40;

      // Act
      const usuario = userService.createUser(nome, email, idade, true);

      // Assert
      expect(usuario).toMatchObject({ nome, email, idade, isAdmin: true, status: 'ativo' });
    });

    test('aceita um usuário com exatamente 18 anos', () => {
      // Arrange
      const idade = 18;

      // Act
      const usuario = userService.createUser('Adulto', 'adulto@email.com', idade);

      // Assert
      expect(usuario.idade).toBe(18);
      expect(usuario.status).toBe('ativo');
    });

    test('rejeita um usuário menor de idade com a mensagem esperada', () => {
      // Arrange
      const nome = 'Menor';
      const email = 'menor@email.com';
      const idade = 17;

      // Act: a chamada é adiada para o matcher observar a exceção.
      const criarUsuario = () => userService.createUser(nome, email, idade);

      // Assert
      expect(criarUsuario).toThrow(new Error('O usuário deve ser maior de idade.'));
    });

    test('rejeita a criação sem nome', () => {
      // Arrange
      const nome = '';

      // Act
      const criarUsuario = () => userService.createUser(nome, 'alice@email.com', 28);

      // Assert
      expect(criarUsuario).toThrow(new Error('Nome, email e idade são obrigatórios.'));
    });

    test('rejeita a criação sem email', () => {
      // Arrange
      const email = '';

      // Act
      const criarUsuario = () => userService.createUser('Alice', email, 28);

      // Assert
      expect(criarUsuario).toThrow(new Error('Nome, email e idade são obrigatórios.'));
    });

    test('rejeita a criação sem idade', () => {
      // Arrange
      const idade = undefined;

      // Act
      const criarUsuario = () => userService.createUser('Alice', 'alice@email.com', idade);

      // Assert
      expect(criarUsuario).toThrow(new Error('Nome, email e idade são obrigatórios.'));
    });
  });

  describe('getUserById', () => {
    test('busca pelo ID e retorna os dados do usuário cadastrado', () => {
      // Arrange
      const usuario = userService.createUser('Alice', 'alice@email.com', 28);

      // Act
      const encontrado = userService.getUserById(usuario.id);

      // Assert
      expect(encontrado).toMatchObject({
        id: usuario.id,
        nome: 'Alice',
        email: 'alice@email.com',
        idade: 28,
        isAdmin: false,
        createdAt: expect.any(Date),
        status: 'ativo',
      });
    });

    test('retorna null para um ID não cadastrado', () => {
      // Arrange
      const id = 'usuario-inexistente';

      // Act
      const encontrado = userService.getUserById(id);

      // Assert
      expect(encontrado).toBeNull();
    });
  });

  describe('deactivateUser', () => {
    test('desativa um usuário comum e mantém seu cadastro consultável', () => {
      // Arrange
      const usuario = userService.createUser('Comum', 'comum@teste.com', 30);

      // Act
      const resultado = userService.deactivateUser(usuario.id);

      // Assert: a consulta pública observa o efeito persistido da ação.
      expect(resultado).toBe(true);
      expect(userService.getUserById(usuario.id)).toMatchObject({
        id: usuario.id,
        nome: 'Comum',
        status: 'inativo',
      });
    });

    test('recusa desativar um administrador e mantém seu status ativo', () => {
      // Arrange
      const usuario = userService.createUser('Admin', 'admin@teste.com', 40, true);

      // Act
      const resultado = userService.deactivateUser(usuario.id);

      // Assert
      expect(resultado).toBe(false);
      expect(userService.getUserById(usuario.id)).toMatchObject({
        id: usuario.id,
        isAdmin: true,
        status: 'ativo',
      });
    });

    test('retorna false ao tentar desativar um ID não cadastrado', () => {
      // Arrange
      const id = 'usuario-inexistente';

      // Act
      const resultado = userService.deactivateUser(id);

      // Assert
      expect(resultado).toBe(false);
    });
  });

  describe('generateUserReport', () => {
    test('identifica o relatório de usuários pelo título inicial', () => {
      // Arrange: o banco foi limpo pelo beforeEach.

      // Act
      const relatorio = userService.generateUserReport();

      // Assert: decoração e espaços antes do título podem variar.
      expect(relatorio).toMatch(/^\W*Relatório de Usuários/u);
    });

    test('informa ID, nome e status de um usuário cadastrado', () => {
      // Arrange
      const usuario = userService.createUser('Alice', 'alice@email.com', 28);

      // Act
      const relatorio = userService.generateUserReport();

      // Assert
      expect(relatorio).toContain(usuario.id);
      expect(relatorio).toContain('Alice');
      expect(relatorio).toMatch(/\bativo\b/u);
    });

    test('inclui todos os usuários cadastrados no relatório', () => {
      // Arrange
      const alice = userService.createUser('Alice', 'alice@email.com', 28);
      const bob = userService.createUser('Bob', 'bob@email.com', 32);

      // Act
      const relatorio = userService.generateUserReport();

      // Assert
      expect(relatorio).toContain(alice.id);
      expect(relatorio).toContain('Alice');
      expect(relatorio).toContain(bob.id);
      expect(relatorio).toContain('Bob');
    });

    test('informa o status inativo de um usuário desativado', () => {
      // Arrange
      const usuario = userService.createUser('Alice', 'alice@email.com', 28);
      userService.deactivateUser(usuario.id);

      // Act
      const relatorio = userService.generateUserReport();

      // Assert
      expect(relatorio).toContain(usuario.id);
      expect(relatorio).toContain('Alice');
      expect(relatorio).toMatch(/\binativo\b/u);
    });

    test('informa a ausência de usuários quando não há cadastros', () => {
      // Arrange: o banco foi limpo pelo beforeEach.

      // Act
      const relatorio = userService.generateUserReport();

      // Assert
      expect(relatorio).toContain('Nenhum usuário cadastrado.');
    });
  });
});
