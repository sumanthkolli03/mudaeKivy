#TODO: hover button for info -> asyncio image tooltips <- L
#TODO: make it so scrollview lets me see all items nad not just like 5 <- L
#TODO: make dabstring copyable, format it not inhumanely <- W, then L

import subprocess
from kivy.app import App 
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from functools import partial as partial #when you press a button, it sends None as the args to allow the .bind() to work; this is useful to send actual args to other screens


class MudaeApp(App):
    def build(self):
        sm = ScreenManagement(transition=NoTransition())
        sm.add_widget(InputScreen(name='Input'))
        sm.add_widget(CheckListScreen(name='Checklist'))
        sm.add_widget(Retry(name='Retry'))
        return sm

class ScreenManagement(ScreenManager):
    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)


class InputScreen(Screen):
    def __init__(self, **kwargs):
        super(InputScreen, self).__init__(**kwargs)
        Window.size = (1000, 800)
        layout = StackLayout()
        self.add_widget(layout)

        layout.add_widget(Label(text="Enter Mudae Stuff here", size_hint = (1, 0.034), pos_hint = {"top": 1}))
        self.mudaeRaw = TextInput(hint_text="y/n's harem...", size_hint = (1, 0.9))
        layout.add_widget(self.mudaeRaw)
        button1 = Button(text="OK", size_hint = (1, 0.066))
        layout.add_widget(button1)
        button1.bind(on_press=self.rawConfirm)

    def rawConfirm(self, btn):
        """recreates CheckListScreen with given input"""
        self.mudaeSorted = sortList(self.mudaeRaw.text)
        if "you suck" in self.mudaeSorted:
            self.manager.get_screen('Retry').update(self.mudaeSorted) #updates Retry , goes to retry
            self.manager.current = 'Retry'
        else:
            self.manager.get_screen('Checklist').update(self.mudaeSorted) #updates CheckListScreen, goes to CheckListScreen
            self.manager.current = 'Checklist'


class CheckListScreen(Screen):
    """main action screen, user chooses which characters here"""

    def __init__(self, **kwargs):
        super(CheckListScreen, self).__init__(**kwargs)

    def back(self, btn):
        self.manager.current = "Input"
        self.clear_widgets()
        self.ids["CheckListLayout"].clear_widgets()
        self.ids["AvailBox"].clear_widgets()
        self.ids["ChosenBox"].clear_widgets()

    def update(self, mudaeSorted):
        """recreates CheckListScreen (from rawConfirm)"""

        global acceptedString, kaCount
        acceptedString = ["$divorceallbut"]
        kaCount = 0

        layout = FloatLayout(size = (1000,800))
        Window.size = (1000, 800)
        self.ids["CheckListLayout"] = layout
        self.add_widget(layout)

        scrollvleft = ScrollView(size_hint=(0.5,0.895), size=(Window.width, Window.height), pos_hint = {"left":1, "top":1}) #BUG: Does scrollview go in Grid? Current example is Grid in scrollview
        layout.add_widget(scrollvleft)
        availBox = GridLayout(cols = 1, size_hint = (0.99,None), size=(Window.width * 0.5, Window.height))
        self.ids["AvailBox"] = availBox
        scrollvleft.add_widget(availBox)

        scrollvright = ScrollView(size_hint=(0.5,0.895), size=(Window.width, Window.height), pos_hint = {"right":1, "top":1})
        layout.add_widget(scrollvright)
        chosenBox = GridLayout(cols = 1, size_hint = (0.99,None), size=(Window.width * 0.5, Window.height))
        self.ids["ChosenBox"] = chosenBox
        scrollvright.add_widget(chosenBox)

        backButton = Button(text="<= Back (THIS WILL RESET EVERYTHING!)", size_hint = (0.5,0.05), pos_hint = {"left":1, "bottom":1})
        layout.add_widget(backButton)
        backButton.bind(on_press = self.back)

        acceptAllButton = Button(text = "Divorce All", size_hint = (0.25, 0.05), pos_hint = {"x":0 ,"y":0.05 })
        layout.add_widget(acceptAllButton)
        acceptAllButton.bind(on_press = partial(self.acceptAll, "", mudaeSorted))

        removeAllButton = Button(text = "Keep All", size_hint = (0.25, 0.05), pos_hint = {"x":0.25 ,"y":0.05 })
        layout.add_widget(removeAllButton)
        removeAllButton.bind(on_press = partial(self.removeAll, "", mudaeSorted))

        copyButton = Button(text = "copy", size_hint = (0.25, 0.05), pos_hint = {"x":0.5, "y":0.05})
        layout.add_widget(copyButton)
        copyButton.bind(on_press = self.copyButtonCall)

        self.acceptedStringLabel = Label(
            text = "".join(acceptedString),
            size_hint = (0.25,0.03), pos_hint = {"right":1, "bottom":1}
        )
        layout.add_widget(self.acceptedStringLabel) #BUG: incredibly broken, fixable but scrollview broke me

        self.kaCounter = Label(
            text = "Total Kakera: "+ str(kaCount),
            size_hint = (0.15,0.07),
            pos_hint = {"x":0.85, "y":0.05}
        )
        layout.add_widget(self.kaCounter)

        for x in mudaeSorted:
            characterAvail = Button(text = f"{x}: {mudaeSorted[x]} kakera", size=(Window.width, Window.height*0.2))
            self.ids[x] = characterAvail
            availBox.add_widget(characterAvail) #BUG: left allign characters
            characterAvail.bind(on_press = partial(self.acceptCharacter, "", (x, mudaeSorted[x])))

    def copyButtonCall(self, btn):
        try:
            copy2clip(self.acceptedStringLabel.text)
        except ValueError as error:
            print(error)
            pass
        except TypeError as error:
            print(error)
            pass

    def acceptCharacter(self, btn, *args):
        """accepts characters -> moves them to accepted list, adds to kaCounter and dabString"""
        Window.size = (1000, 800)
        (charName, charKa), _ = args
        self.ids["AvailBox"].remove_widget(self.ids[charName])
        charNameAccepted = Button(text = f"{charName}: {charKa} kakera", size = ((Window.width*0.5), (Window.height*0.2)))
        self.ids[charName] = charNameAccepted
        charNameAccepted.bind(on_press = partial(self.removeCharacter, "", (charName, charKa)))
        self.ids["ChosenBox"].add_widget(charNameAccepted)

        global acceptedString, kaCount
        acceptedString.append(charName)
        self.acceptedStringLabel.text = " $".join(acceptedString)
        kaCount += charKa
        self.kaCounter.text = "Total Kakera: "+ str(kaCount)

    def acceptAll(self, btn, *args):
        """accepts all characters by deleting all current entries and rebuilding them, updates kaCount and dabstring"""
        mudaeSorted, _ = args
        try:
            self.ids["AvailBox"].clear_widgets()
            self.ids["ChosenBox"].clear_widgets()
            global acceptedString, kaCount
            acceptedString.clear()
            acceptedString.append("$divorceallbut")            
            kaCount = 0

            for char in mudaeSorted:
                charAccepted = Button(text = f"{char}: {mudaeSorted[char]} kakera", size=(Window.width, Window.height*0.2))
                self.ids[char] = charAccepted
                self.ids["ChosenBox"].add_widget(charAccepted) #BUG: left allign characters
                charAccepted.bind(on_press = partial(self.removeCharacter, "", (char, mudaeSorted[char])))
                
                acceptedString.append(char)
                kaCount += mudaeSorted[char]

            self.acceptedStringLabel.text = " $".join(acceptedString)
            self.kaCounter.text = "Total Kakera: "+ str(kaCount)

        except KeyError as error: #REVIEW: built as a test, remove in final version, pop up an error?
            print(error)
            pass

    def removeCharacter(self, btn, *args):
        """accepts characters -> moves them to available list, subtracts from kaCounter and dabString"""
        Window.size = (1000,800)
        (charName, charKa), _ = args
        self.ids["ChosenBox"].remove_widget(self.ids[charName])
        charNameAvailable = Button(text = f"{charName}: {charKa} kakera", size = ((Window.width*0.5), (Window.height*0.2)))
        self.ids[charName] = charNameAvailable
        charNameAvailable.bind(on_press = partial(self.acceptCharacter, "", (charName, charKa)))
        self.ids["AvailBox"].add_widget(charNameAvailable)

        global acceptedString, kaCount
        acceptedString.remove(charName)
        self.acceptedStringLabel.text = " $".join(acceptedString)
        kaCount -= charKa
        self.kaCounter.text = "Total Kakera: "+ str(kaCount)
    
    def removeAll(self, btn, *args):
        """removes all characters by deleting all current entries and rebuilding them, updates kaCount and dabstring"""
        mudaeSorted, _ = args
        try:
            self.ids["AvailBox"].clear_widgets()
            self.ids["ChosenBox"].clear_widgets()
            global acceptedString, kaCount
            acceptedString.clear()
            acceptedString.append("$divorceallbut")
            kaCount = 0

            for char in mudaeSorted:
                characterAvail = Button(text = f"{char}: {mudaeSorted[char]} kakera", size=(Window.width, Window.height*0.2))
                self.ids[char] = characterAvail
                self.ids["AvailBox"].add_widget(characterAvail) #BUG: left allign characters
                characterAvail.bind(on_press = partial(self.acceptCharacter, "", (char, mudaeSorted[char])))

            self.acceptedStringLabel.text = " $".join(acceptedString)
            self.kaCounter.text = "Total Kakera: "+ str(kaCount)

        except KeyError as error: #REVIEW: built as a test, remove in final version, pop up an error?
            print(error)
            pass


class Retry(Screen):
    """redirect screen after a failed input"""

    def __init__(self, **kwargs):
        super(Retry, self).__init__(**kwargs)
        self.textL = Label(text = "L") #this should never show! (built as a test, remove in final version)
        self.add_widget(self.textL)
        button2 = Button(text="OK", size_hint = (1,0.1))
        self.add_widget(button2)
        button2.bind(on_press=self.retry)

    def update(self, mudaeSorted):
        self.textL.text = ("You suck, try again.\n" +
        "Make sure to copy only the characters and kakera values!")

    def retry(self, btn):
        self.manager.current = "Input"


def sortList(mudaeRaw: str) -> dict[str, int]:
    try:
        mudaeRaw = mudaeRaw.strip().split("\n")
        mudaeList = [item.split() for item in mudaeRaw]
        mudaeSorted = {" ".join(_[:-2]):int("".join(_[-2:-1])) for _ in mudaeList}
        return mudaeSorted
    except ValueError as error:
        return "you suck, try again"

def copy2clip(txt):
    cmd='echo '+txt.strip()+'|clip'
    return subprocess.check_call(cmd, shell=True)

if __name__ == '__main__':
    MudaeApp().run()
    