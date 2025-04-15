from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class AIApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Нажми, чтобы поговорить с AI")
        self.button = Button(text="Говорить", on_press=self.speak)
        layout.add_widget(self.label)
        layout.add_widget(self.button)
        return layout

    def speak(self, instance):
        self.label.text = "AI слушает..."
        response = "ddd"  # Используем уже существующую функцию
        self.label.text = f"Ответ AI: {response}"

AIApp().run()
