import os
import sys
import shutil
import psutil
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QFileDialog, QPushButton, QComboBox, QLabel, QCheckBox
app = QtWidgets.QApplication(sys.argv)

class FileOrganizerApp(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle('ファイル整理アプリ')
    self.setGeometry(100, 100, 800, 600)
    self.dark_mode = False
    self.language = '日本語'

    # 言語設定
    self.text_resources = {
        '日本語': {
            'folder_button': 'フォルダーを選択',
            'execute_button': '適用',
            'mode_combo_items': ['ファイル自動振り分け', '重複ファイルの検出'],
            'language_button': '設定',
            'tabs': ['File', 'Mode', 'Tools'],
            'settings_title': '設定',
            'language_label': '言語設定:'
        },
        'English': {
            'folder_button': 'Select Folder',
            'execute_button': 'Apply',
            'mode_combo_items': ['Auto File Sorting', 'Detect Duplicate Files'],
            'language_button': 'Settings',
            'tabs': ['File', 'Mode', 'Tools'],
            'settings_title': 'Settings',
            'language_label': 'Language Settings:'
        }
    }

    # フォルダー情報の表示
    self.drive_info_label = QLabel("", self)
    self.drive_info_label.setFont(QtGui.QFont('Meiryo', 12))
    self.folder_info_label = QLabel("", self)

    self.initialize_ui()

  def update_language_ui(self):
    """UIのテキストを現在の言語に応じて更新"""
    texts = self.text_resources[self.language]

    # 各テキストを更新
    self.folder_button.setText(texts['folder_button'])
    self.execute_button.setText(texts['execute_button'])
    self.mode_combo.clear()
    self.mode_combo.addItems(texts['mode_combo_items'])
    self.language_button.setText(texts['language_button'])

    # タブのタイトルを更新
    self.tabs.setTabText(0, texts['tabs'][0])
    self.tabs.setTabText(1, texts['tabs'][1])
    self.tabs.setTabText(2, texts['tabs'][2])

  def show_language_settings(self):
    """設定ダイアログの表示"""
    dialog = QtWidgets.QDialog(self)
    texts = self.text_resources[self.language]  # 言語リソースを取得
    dialog.setWindowTitle(texts['settings_title'])
    layout = QVBoxLayout()

    language_label = QLabel(texts['language_label'], self)
    layout.addWidget(language_label)
    language_combo = QComboBox(self)
    language_combo.addItems(['日本語', 'English'])
    language_combo.setCurrentText(self.language)
    language_combo.currentTextChanged.connect(self.change_language)
    layout.addWidget(language_combo)

    dialog.setLayout(layout)
    dialog.exec_()

    # フォルダー情報のラベル
    self.drive_info_label = QLabel("", self)
    self.drive_info_label.setFont(QtGui.QFont('Meiryo', 12))
    self.folder_info_label = QLabel("", self)

    self.initialize_ui()

  def initialize_ui(self):
    self.tabs = QTabWidget(self)
    self.setCentralWidget(self.tabs)

    # File tab
    file_tab = QtWidgets.QWidget()
    file_tab_layout = QVBoxLayout()

    self.icon_label = QtWidgets.QLabel(self)
    pixmap = QtGui.QPixmap("folder.png")
    pixmap = pixmap.scaled(150, 150)
    self.icon_label.setPixmap(pixmap)
    self.icon_label.setAlignment(QtCore.Qt.AlignCenter)   # type: ignore
    file_tab_layout.addWidget(self.icon_label)

    self.folder_button = QPushButton('フォルダーを選択', self)
    self.folder_button.setFont(QtGui.QFont('Meiryo', 12))
    self.folder_button.clicked.connect(self.select_folder)
    file_tab_layout.addWidget(self.folder_button)

    # ドライブとフォルダーの情報を表示
    file_tab_layout.addWidget(self.drive_info_label)
    file_tab_layout.addWidget(self.folder_info_label)

    file_tab.setLayout(file_tab_layout)
    self.tabs.addTab(file_tab, "File")

    # Mode tab
    mode_tab = QtWidgets.QWidget()
    mode_tab_layout = QtWidgets.QVBoxLayout(mode_tab)

    image_layout = QtWidgets.QHBoxLayout()
    for image_path in ["file.png", "yazirusi.png", "files.png"]:  # Use actual image paths
      icon_label = QtWidgets.QLabel(self)
      pixmap = QtGui.QPixmap(image_path)
      pixmap = pixmap.scaled(150, 150)
      icon_label.setPixmap(pixmap)
      icon_label.setAlignment(QtCore.Qt.AlignCenter)  # type: ignore
      image_layout.addWidget(icon_label)

    mode_tab_layout.addLayout(image_layout)

    self.mode_combo = QtWidgets.QComboBox(self)
    self.mode_combo.addItems(['ファイル自動振り分け', '重複ファイルの検出'])
    self.mode_combo.setFont(QtGui.QFont('Meiryo', 12))
    mode_tab_layout.addWidget(self.mode_combo)

    self.execute_button = QtWidgets.QPushButton('適用', self)
    self.execute_button.setFont(QtGui.QFont('Meiryo', 12))
    mode_tab_layout.addWidget(self.execute_button)

    mode_tab.setLayout(mode_tab_layout)
    self.tabs.addTab(mode_tab, "Mode")

    # Tools
    tools_tab = QtWidgets.QWidget()
    tools_tab_layout = QVBoxLayout()

    self.settings_icon_label = QtWidgets.QLabel(self)
    settings_pixmap = QtGui.QPixmap("Settings.png")
    settings_pixmap = settings_pixmap.scaled(
        150, 150)
    self.settings_icon_label.setPixmap(settings_pixmap)
    self.settings_icon_label.setAlignment(QtCore.Qt.AlignCenter)  # type: ignore
    tools_tab_layout.addWidget(self.settings_icon_label)

    self.language_button = QPushButton('設定', self)
    self.language_button.clicked.connect(self.show_settings)
    self.language_button.setFont(QtGui.QFont('Meiryo', 12))
    tools_tab_layout.addWidget(self.language_button)
    tools_tab.setLayout(tools_tab_layout)
    self.tabs.addTab(tools_tab, "Tools")

    # C drive info
    c_drive_info_label = QtWidgets.QLabel(self)
    c_drive_usage = psutil.disk_usage('C:\\')
    c_drive_info = (f"Total: {c_drive_usage.total // (2**30)} GB, "
                    f"Used: {c_drive_usage.used // (2**30)} GB, "
                    f"Free: {c_drive_usage.free // (2**30)} GB, "
                    f"Percent: {c_drive_usage.percent}%")
    c_drive_info_label.setText(f"C Drive Info: {c_drive_info}")
    font = QtGui.QFont("Arial", 12)
    c_drive_info_label.setFont(font)
    tools_tab_layout.addWidget(c_drive_info_label)

    # 起動時にドライブ情報を表示
    self.update_drive_info()

  def update_drive_info(self):
    # Cドライブサイズ情報
    total, used, free = shutil.disk_usage("C:/")
    total_gb = total // (2**30)
    used_gb = used // (2**30)
    free_gb = free // (2**30)
    self.drive_info_label.setText(f"Cドライブ: 使用中: {used_gb}GB, 空き: {
                                  free_gb}GB, 合計: {total_gb}GB")

  def update_folder_info(self, folder_path):
    # 選択したフォルダーのファイル数を表示
    file_count = sum(len(files) for _, _, files in os.walk(folder_path))
    self.folder_info_label.setText(
        f"選択したフォルダー: {folder_path}\nファイル数: {file_count}")

  def select_folder(self):
    folder_path = QFileDialog.getExistingDirectory(self, 'フォルダーを選択', '')
    if folder_path:
      self.update_folder_info(folder_path)
      if self.mode_combo.currentText() == 'ファイル自動振り分け':
        self.organize_files(folder_path)
      elif self.mode_combo.currentText() == '重複ファイルの検出':
        self.detect_duplicates(folder_path)

  def organize_files(self, folder_path):
    categories = {
        'images': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'movies': ['mp4', 'mov', 'avi', 'mkv'],
        'musics': ['mp3', 'wav', 'flac'],
        'archives': ['zip', 'rar', '7z', 'tar.gz'],
        'spreadsheets': ['xls', 'xlsx', 'csv', 'ods'],
        'presentations': ['ppt', 'pptx', 'odp'],
        'code': ['py', 'js', 'html', 'css', 'c', 'cpp',
                 'java', 'rb', 'php'],
        'documents': ['pdf', 'doc', 'docx', 'txt', 'odt']
    }

    for category, extensions in categories.items():
      category_path = os.path.join(folder_path, category)
      if not os.path.exists(category_path):
        os.makedirs(category_path)

      for root, _, files in os.walk(folder_path):
        if root.startswith(category_path):
          continue  # すでに整理されたフォルダーは無視

        for file in files:
          if file.split('.')[-1].lower() in extensions:
            source_file = os.path.join(root, file)
            destination_file = os.path.join(category_path, file)
            shutil.move(source_file, destination_file)
            print(f"{file} を {category} フォルダーに移動しました。")

  def detect_duplicates(self, folder_path):
    files_seen = {}
    duplicates_found = []

    for root, _, files in os.walk(folder_path):
      for file in files:
        file_path = os.path.join(root, file)
        file_size = os.path.getsize(file_path)
        file_key = (file_size, file)

        if file_key in files_seen:
          duplicates_found.append(file_path)
          print(f"重複ファイル: {file_path} は {files_seen[file_key]} と同じです")
        else:
          files_seen[file_key] = file_path

    if not duplicates_found:
      QtWidgets.QMessageBox.information(self, "結果", "重複ファイルは見つかりませんでした。")
    else:
      QtWidgets.QMessageBox.information(
          self, "結果", f"{len(duplicates_found)}個の重複ファイルが見つかりました。コンソールを確認してください。")

  def show_settings(self):
    dialog = QtWidgets.QDialog(self)
    dialog.setWindowTitle("設定")
    layout = QVBoxLayout()

    language_label = QLabel('言語設定:', self)
    layout.addWidget(language_label)
    language_combo = QComboBox(self)
    language_combo.addItems(['日本語', 'English'])
    language_combo.setCurrentText(self.language)
    language_combo.currentTextChanged.connect(self.change_language)
    layout.addWidget(language_combo)

    dialog.setLayout(layout)
    dialog.exec_()

  def change_language(self, text):
    self.language = text
    # UI更新メソッドを呼び出してUIテキストを更新
    self.update_language_ui()

  def toggle_dark_mode(self, state):
    self.dark_mode = bool(state)
    self.apply_stylesheet()

def main():
  import sys
  app = QtWidgets.QApplication(sys.argv)
  window = FileOrganizerApp()
  window.show()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
