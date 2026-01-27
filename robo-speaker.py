import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

print('Welcome to PakSpeaker---')

while True:
    x = input('What you want to say ?:: ').strip()

    if not x:
        continue

    if x.lower() == 'exit':
        engine.say("See you next time")
        engine.runAndWait()
        engine.stop()
        break

    engine.stop()          # 🔥 clears queue (important)
    engine.say(x)
    engine.runAndWait()


# import pyttsx3
#
# engine = pyttsx3.init()
# engine.say("Hello, this is a test")
# engine.runAndWait()
