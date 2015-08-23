import urwid
import random
import csv
import logging
import os


class LuckyDrawController(object):
    def __init__(self):
        logging.basicConfig(filename="lucky.log", level=logging.DEBUG)
        self.text = urwid.BigText(u'Let\'s Draw', urwid.font.HalfBlock5x4Font())
        self.padding = urwid.Padding(self.text, 'center', width='clip')
        self.fill = urwid.Filler(self.padding)
        self.count = 0
        self.footer = urwid.Text("Press enter to save and choose new winner, press ESC to choose a new one without saving, press s to save and quit")
        self.ftr = urwid.AttrWrap(self.footer, "footer")
        self.frame = urwid.Frame(footer=self.ftr, body=self.fill)

        self.mainloop = urwid.MainLoop(self.frame, unhandled_input=self.q_to_exit)
        self.csv_reader = csv.reader(open("attendee_email.csv"))
        self.data = []
        for item in self.csv_reader:
            self.data.append(tuple(item)) 
        self.selected = set()
        self.winner = ""
        self.winner_email = ""
        if os.path.isfile("result.csv"):
            f = open("result.csv","rb")
            result_file = csv.reader(f)
            for entry in result_file:
                self.selected.add((entry[0], entry[1]))
            f.close()
        self.result_file = csv.writer(open("result.csv", "ab"))
        self.update_interval = 0.1  

    def change_text(self, loop=None, user_data=None):
        if self.count > 10:
            self.mainloop.remove_alarm(self.alarm)
            self.text.set_text("WINNER!!!! %s" % self.winner)
            self.selected.add((self.winner, self.winner_email))
        else:
            name, email = random.choice(self.data)
            while (name, email) in self.selected:
                name, email = random.choice(self.data)
                
            self.text.set_text(name)
            self.winner = name
            self.winner_email = email
    
            self.alarm = self.mainloop.set_alarm_in(self.update_interval, self.change_text, None)
            self.count = self.count + 1

    def q_to_exit(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        if key in ('s', 'S'):
            if self.winner:
                self.result_file.writerow([self.winner, self.winner_email])
            raise urwid.ExitMainLoop()
        if key == 'enter':
            self.count = 0
            if self.winner:
                self.result_file.writerow([self.winner, self.winner_email])
                logging.info("%s, %s" % (self.winner, self.winner_email))
            self.alarm = self.mainloop.set_alarm_in(self.update_interval, self.change_text, None)
        if key == 'esc':
            self.count = 0
            self.alarm = self.mainloop.set_alarm_in(self.update_interval, self.change_text, None)
            

    def run(self):
        self.mainloop.run()
       
if __name__ == "__main__":
    controller = LuckyDrawController()
    controller.run()
