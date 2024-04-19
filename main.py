import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, Rectangle, RoundedRectangle
from fuzzywuzzy import process
import json
import zipfile

# Caminho dinâmico para o diretório do arquivo .py
base_path = os.path.dirname(os.path.abspath(__file__))

resource_add_path(os.path.join(base_path, 'fonte', 'static'))
LabelBase.register(name='Noto', fn_regular='NotoSansJP-Regular.ttf')

class DictionaryApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        with layout.canvas.before:
            Color(0, 0, 0, 1)  # Black color for background
            self.rect = Rectangle(size=layout.size, pos=layout.pos)

        layout.bind(size=self._update_rect, pos=self._update_rect)

        self.input = TextInput(hint_text='Insira a palavra em japonês', size_hint=(1, 0.2), font_name='Noto', background_color=(1, 1, 1, 1))
        layout.add_widget(self.input)

        self.button = Button(text='Buscar Tradução', size_hint=(1, 0.1), font_name='Noto')
        with self.button.canvas.before:
            Color(1, 1, 1, 1)  # White color for button background
            RoundedRectangle(size=self.button.size, pos=self.button.pos, radius=[10])
        self.button.bind(on_press=self.on_search_pressed, size=self._update_button_background, pos=self._update_button_background)
        layout.add_widget(self.button)

        self.scroll_view = ScrollView(size_hint=(1, 0.6), do_scroll_x=False)
        self.label = Label(text='Aqui aparecerão as informações completas', font_name='Noto', size_hint_y=None,
                           text_size=(layout.width, None), halign='left', valign='top', color=(1, 1, 1, 1))
        self.label.bind(size=lambda *x: setattr(self.label, 'text_size', (self.label.width, None)))
        self.scroll_view.add_widget(self.label)
        layout.add_widget(self.scroll_view)

        self.copy_button = Button(text='Copiar Traduções', size_hint=(1, 0.05), font_name='Noto')
        with self.copy_button.canvas.before:
            Color(1, 1, 1, 1)  # White color for button background
            RoundedRectangle(size=self.copy_button.size, pos=self.copy_button.pos, radius=[10])
        self.copy_button.bind(on_press=self.on_copy_pressed, size=self._update_button_background, pos=self._update_button_background)
        layout.add_widget(self.copy_button)

        # Caminhos atualizados para os arquivos zip
        self.terms = self.load_terms([os.path.join(base_path, 'dictionary', 'kireicake.zip'),
                                      os.path.join(base_path, 'dictionary', 'jmnedict.zip')])
        return layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_button_background(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 1, 1, 1)  # White color
            RoundedRectangle(size=instance.size, pos=instance.pos, radius=[10])

    def load_terms(self, paths):
        terms = {}
        for path in paths:
            with zipfile.ZipFile(path, 'r') as z:
                for filename in z.namelist():
                    if filename.startswith("term_bank_") and filename.endswith(".json"):
                        with z.open(filename) as file:
                            data = json.load(file)
                            for entry in data:
                                japanese_word = entry[0]
                                reading = entry[1]
                                translations = entry[5]
                                if japanese_word in terms:
                                    terms[japanese_word]['translations'].extend(translations)
                                else:
                                    terms[japanese_word] = {'reading': reading, 'translations': translations}
        return terms

    def on_search_pressed(self, instance):
        japanese_word = self.input.text.strip()
        self.search_translation(japanese_word)

    def search_translation(self, word):
        result = self.terms.get(word, None)
        if not result:
            closest_match, score = process.extractOne(word, self.terms.keys())
            if score > 80:
                result = self.terms.get(closest_match)
                self.translation_text = f"Palavra aproximada: '{closest_match}'\nLeitura: {result['reading']}\nTraduções: {', '.join(result['translations'])}"
            else:
                self.translation_text = "Nenhuma tradução encontrada."
        else:
            self.translation_text = f"Palavra: '{word}'\nLeitura: {result['reading']}\nTraduções: {', '.join(result['translations'])}"

        self.update_label(self.translation_text)

    def on_copy_pressed(self, instance):
        clean_text = self.translation_text.replace("[b]", "").replace("[/b]", "")
        Clipboard.copy(clean_text)
        self.label.text = 'Traduções copiadas para a área de transferência!'

    def update_label(self, text):
        self.label.text = text

if __name__ == '__main__':
    DictionaryApp().run()
