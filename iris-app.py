import sys
import firebase_admin
from firebase_admin import credentials, firestore, auth
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QCheckBox, QScrollArea, QFrame,
                             QMessageBox, QStackedWidget)
from PyQt5.QtCore import Qt
from datetime import datetime

# --- Configuração do Firebase ---
# Substitua pelo caminho do seu arquivo de credenciais do Firebase
try:
    cred = credentials.Certificate("caminho/para/seu/firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Erro ao inicializar o Firebase: {e}")
    sys.exit()

# --- Classes de Componentes ---

class PersonagensApp(QWidget):
    def __init__(self, parent=None, isAdmin=False):
        super().__init__(parent)
        self.isAdmin = isAdmin
        self.personagens = []
        self.idEditando = None
        self.initUI()
        self.load_personagens()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        
        self.personagens_container = QScrollArea()
        self.personagens_container.setWidgetResizable(True)
        self.personagens_list_widget = QWidget()
        self.personagens_list_layout = QVBoxLayout(self.personagens_list_widget)
        self.personagens_container.setWidget(self.personagens_list_widget)
        self.main_layout.addWidget(self.personagens_container)

        if self.isAdmin:
            self.admin_ui = QFrame()
            self.admin_layout = QVBoxLayout(self.admin_ui)
            self.admin_ui.setFrameShape(QFrame.StyledPanel)
            self.admin_layout.addWidget(QLabel('<h3>Administrar Personagens:</h3>'))
            self.admin_layout.addWidget(QLabel('Nome:'))
            self.nome_input = QLineEdit()
            self.admin_layout.addWidget(self.nome_input)
            self.admin_layout.addWidget(QLabel('Descrição:'))
            self.desc_input = QLineEdit()
            self.admin_layout.addWidget(self.desc_input)
            self.admin_layout.addWidget(QLabel('URL da imagem:'))
            self.url_input = QLineEdit()
            self.admin_layout.addWidget(self.url_input)
            self.visibility_checkbox = QCheckBox('Visível para os jogadores:')
            self.visibility_checkbox.setChecked(True)
            self.admin_layout.addWidget(self.visibility_checkbox)
            self.error_label = QLabel('')
            self.error_label.setStyleSheet("color: red;")
            self.admin_layout.addWidget(self.error_label, alignment=Qt.AlignCenter)
            self.buttons_layout = QHBoxLayout()
            self.add_button = QPushButton('Adicionar')
            self.add_button.clicked.connect(self.adicionar_personagem)
            self.buttons_layout.addWidget(self.add_button)
            self.edit_button = QPushButton('Confirmar Edição')
            self.edit_button.clicked.connect(self.confirmar_edicao)
            self.edit_button.setVisible(False)
            self.buttons_layout.addWidget(self.edit_button)
            self.cancel_button = QPushButton('Cancelar Edição')
            self.cancel_button.clicked.connect(self.cancelar_edicao)
            self.cancel_button.setVisible(False)
            self.buttons_layout.addWidget(self.cancel_button)
            self.admin_layout.addLayout(self.buttons_layout)
            self.main_layout.addWidget(self.admin_ui)

    def load_personagens(self):
        for i in reversed(range(self.personagens_list_layout.count())):
            self.personagens_list_layout.itemAt(i).widget().setParent(None)
        
        personagens_doc_ref = db.collection('personagens').document('personagens')
        personagens_doc = personagens_doc_ref.get()

        if personagens_doc.exists:
            self.personagens = personagens_doc.to_dict().get('personagens', [])
        else:
            self.personagens = []

        for i, personagem in enumerate(self.personagens):
            if personagem.get('visivel', True) or self.isAdmin:
                card = self.create_char_card(personagem, i)
                self.personagens_list_layout.addWidget(card)
        
        self.personagens_list_layout.addStretch()

    def create_char_card(self, personagem, i):
        card = QFrame()
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(QLabel(f'<b>{personagem.get("nome", "Sem Nome")}</b>'))
        card_layout.addWidget(QLabel(personagem.get("descricao", "Sem Descrição")))
        
        if self.isAdmin:
            buttons_layout = QHBoxLayout()
            edit_button = QPushButton('Editar')
            edit_button.clicked.connect(lambda: self.editar_personagem(i))
            buttons_layout.addWidget(edit_button)
            remove_button = QPushButton('Remover')
            remove_button.clicked.connect(lambda: self.remover_personagem(i))
            buttons_layout.addWidget(remove_button)
            up_button = QPushButton('Mover ↑')
            up_button.clicked.connect(lambda: self.mover_personagem(i, -1))
            buttons_layout.addWidget(up_button)
            down_button = QPushButton('Mover ↓')
            down_button.clicked.connect(lambda: self.mover_personagem(i, 1))
            buttons_layout.addWidget(down_button)
            card_layout.addLayout(buttons_layout)
        return card

    def save(self):
        personagens_doc_ref = db.collection('personagens').document('personagens')
        personagens_doc_ref.set({'personagens': self.personagens})
        self.load_personagens()

    def mover_personagem(self, i, direcao):
        if (i == 0 and direcao == -1) or (i == len(self.personagens) - 1 and direcao == 1):
            return
        self.personagens[i], self.personagens[i + direcao] = self.personagens[i + direcao], self.personagens[i]
        self.save()

    def editar_personagem(self, i):
        self.idEditando = i
        personagem = self.personagens[i]
        self.nome_input.setText(personagem.get('nome', ''))
        self.desc_input.setText(personagem.get('descricao', ''))
        self.url_input.setText(personagem.get('imagem', ''))
        self.visibility_checkbox.setChecked(personagem.get('visivel', True))
        self.add_button.setVisible(False)
        self.edit_button.setVisible(True)
        self.cancel_button.setVisible(True)

    def cancelar_edicao(self):
        self.idEditando = None
        self.nome_input.clear()
        self.desc_input.clear()
        self.url_input.clear()
        self.visibility_checkbox.setChecked(True)
        self.add_button.setVisible(True)
        self.edit_button.setVisible(False)
        self.cancel_button.setVisible(False)

    def confirmar_edicao(self):
        if not self.nome_input.text() or not self.desc_input.text() or not self.url_input.text():
            self.error_label.setText("Preencha todos os campos.")
            return

        self.personagens[self.idEditando] = {
            'nome': self.nome_input.text(),
            'descricao': self.desc_input.text(),
            'imagem': self.url_input.text(),
            'visivel': self.visibility_checkbox.isChecked()
        }
        self.cancelar_edicao()
        self.error_label.setText("")
        self.save()

    def adicionar_personagem(self):
        if not self.nome_input.text() or not self.desc_input.text() or not self.url_input.text():
            self.error_label.setText("Preencha todos os campos.")
            return
        
        novo_personagem = {
            'nome': self.nome_input.text(),
            'descricao': self.desc_input.text(),
            'imagem': self.url_input.text(),
            'visivel': self.visibility_checkbox.isChecked()
        }
        self.personagens.append(novo_personagem)
        self.nome_input.clear()
        self.desc_input.clear()
        self.url_input.clear()
        self.visibility_checkbox.setChecked(True)
        self.error_label.setText("")
        self.save()

    def remover_personagem(self, i):
        reply = QMessageBox.question(self, 'Confirmar Exclusão',
                                     f'Você deseja DELETAR o personagem {self.personagens[i]["nome"]}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.personagens.pop(i)
            self.save()

class ResumosApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.load_summaries()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(QLabel('<h3>Resumos de Sessão</h3>'))
        self.main_layout.addWidget(QLabel('<p>Aqui você pode ver os resumos das sessões anteriores publicados pelo Mestre.</p>'))
        
        self.summaries_container = QScrollArea()
        self.summaries_container.setWidgetResizable(True)
        self.summaries_list_widget = QWidget()
        self.summaries_list_layout = QVBoxLayout(self.summaries_list_widget)
        self.summaries_container.setWidget(self.summaries_list_widget)
        self.main_layout.addWidget(self.summaries_container)

    def load_summaries(self):
        for i in reversed(range(self.summaries_list_layout.count())):
            self.summaries_list_layout.itemAt(i).widget().setParent(None)

        summaries_ref = db.collection("sessionSummaries").order_by("timestamp", direction=firestore.Query.DESCENDING)
        
        summaries_found = False
        for doc in summaries_ref.stream():
            summary = doc.to_dict()
            card = self.create_summary_card(summary)
            self.summaries_list_layout.addWidget(card)
            summaries_found = True
        
        if not summaries_found:
            self.summaries_list_layout.addWidget(QLabel('<p>Nenhum resumo de sessão disponível.</p>'))
        
        self.summaries_list_layout.addStretch()

    def create_summary_card(self, summary):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card_layout = QVBoxLayout(card)
        title = summary.get('title', 'Sem Título')
        content = summary.get('content', 'Sem conteúdo.').replace('\n', '<br>')
        createdBy = summary.get('createdBy', 'Mestre')
        timestamp = summary.get('timestamp')
        
        card_layout.addWidget(QLabel(f'<h4 style="color:#6f42c1;">{title}</h4>'))
        card_layout.addWidget(QLabel(f'<p>{content}</p>'))
        card_layout.addWidget(QLabel(f'<small style="text-align:right; color:#6c757d;">Publicado por: {createdBy} em {self.format_timestamp(timestamp)}</small>', alignment=Qt.AlignRight))
        return card

    def format_timestamp(self, timestamp):
        if not timestamp:
            return ''
        if isinstance(timestamp, datetime):
            return timestamp.strftime('%d de %B de %Y, %H:%M')
        return datetime.fromtimestamp(timestamp / 1000).strftime('%d de %B de %Y, %H:%M')

class RegisterApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.form_widget = QFrame()
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.setAlignment(Qt.AlignCenter)
        self.form_widget.setStyleSheet("border: 2px solid gray; border-radius: 5px; padding: 10px;")
        self.form_layout.addWidget(QLabel('<h3>Crie sua conta:</h3>', alignment=Qt.AlignCenter))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('E-mail')
        self.form_layout.addWidget(self.email_input)
        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText('Senha')
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.form_layout.addWidget(self.senha_input)
        self.confirmar_senha_input = QLineEdit()
        self.confirmar_senha_input.setPlaceholderText('Confirme a senha')
        self.confirmar_senha_input.setEchoMode(QLineEdit.Password)
        self.form_layout.addWidget(self.confirmar_senha_input)
        self.error_label = QLabel('')
        self.error_label.setStyleSheet("color: red;")
        self.form_layout.addWidget(self.error_label, alignment=Qt.AlignCenter)
        self.register_button = QPushButton('Registrar')
        self.register_button.clicked.connect(self.handle_register)
        self.form_layout.addWidget(self.register_button)
        self.login_link = QLabel('Já tem uma conta? <a href="#">Faça login aqui</a>')
        self.login_link.setOpenExternalLinks(False)
        self.login_link.linkActivated.connect(self.parent.show_login)
        self.form_layout.addWidget(self.login_link, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.form_widget)

    def handle_register(self):
        email = self.email_input.text()
        senha = self.senha_input.text()
        confirmarSenha = self.confirmar_senha_input.text()
        self.error_label.setText('')

        if senha != confirmarSenha:
            self.error_label.setText('As senhas não coincidem.')
            return
        if len(senha) < 6:
            self.error_label.setText('A senha deve ter pelo menos 6 caracteres.')
            return

        try:
            auth.create_user(email=email, password=senha)
            QMessageBox.information(self, 'Sucesso', f'Usuário {email} registrado com sucesso!')
            self.parent.show_dashboard()
        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                self.error_label.setText('Este e-mail já está em uso.')
            elif "INVALID_EMAIL" in error_message:
                self.error_label.setText('O formato do e-mail é inválido.')
            elif "WEAK_PASSWORD" in error_message:
                self.error_label.setText('A senha é muito fraca.')
            else:
                self.error_label.setText('Ocorreu um erro ao tentar registrar. Tente novamente.')

class LoginApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
    
    def initUI(self):
        # UI de login simples para simular a navegação
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.form_widget = QFrame()
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.addWidget(QLabel('<h3>Faça login:</h3>', alignment=Qt.AlignCenter))
        self.login_button = QPushButton('Login (simulado)')
        self.login_button.clicked.connect(self.parent.show_dashboard)
        self.form_layout.addWidget(self.login_button)
        self.register_link = QLabel('Não tem uma conta? <a href="#">Crie uma aqui</a>')
        self.register_link.linkActivated.connect(self.parent.show_register)
        self.form_layout.addWidget(self.register_link, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.form_widget)


# --- Classe Principal para Gerenciar a Navegação ---

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App Svelte em Python")
        self.setGeometry(100, 100, 800, 600)
        
        self.isAdmin = False  # Defina para True se o usuário for administrador
        
        self.stack = QStackedWidget(self)
        
        # Telas do aplicativo
        self.login_page = LoginApp(self)
        self.register_page = RegisterApp(self)
        self.personagens_page = PersonagensApp(self, isAdmin=self.isAdmin)
        self.resumos_page = ResumosApp(self)
        
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)
        self.stack.addWidget(self.personagens_page)
        self.stack.addWidget(self.resumos_page)
        
        # Adicionar botões de navegação
        self.nav_layout = QHBoxLayout()
        self.btn_personagens = QPushButton('Personagens')
        self.btn_personagens.clicked.connect(lambda: self.stack.setCurrentWidget(self.personagens_page))
        self.btn_resumos = QPushButton('Resumos')
        self.btn_resumos.clicked.connect(lambda: self.stack.setCurrentWidget(self.resumos_page))
        self.nav_layout.addWidget(self.btn_personagens)
        self.nav_layout.addWidget(self.btn_resumos)
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(self.nav_layout)
        main_layout.addWidget(self.stack)
        
        # Começa na tela de login
        self.show_login()

    def show_login(self):
        self.stack.setCurrentWidget(self.login_page)

    def show_register(self):
        self.stack.setCurrentWidget(self.register_page)

    def show_dashboard(self):
        # A "dashboard" seria a tela inicial depois do login, com botões para as outras páginas
        # Aqui, vamos mostrar a tela de personagens como a "dashboard"
        self.stack.setCurrentWidget(self.personagens_page)

# --- Execução do Aplicativo ---

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())