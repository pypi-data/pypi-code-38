import os
import gherkan.utils.constants as c

from gherkan.flask_api.raw_text_to_signal import nl_to_signal

# request = {
#     "feature": "robot R4",
#     "feature_desc": "Robot R4 je kolaborativní robot Kuka IIWA. Má za úkol finální kompletaci autíčka. Postupně mu jsou na jeho stanici XX přivezeny zkompletované součásti autíčka. Robotu je nejdříve přivezono chassi autíčka. Následuje body (korba) a jako poslední je přivezena kabina.",
#     "background": "given line is on",
#     "text_raw": "scenario   As soon as robot R1 finished sorting all cubes, shuttle goes to station XXX",
#     "language": "en"
# }

request = {
    "feature" : "Montrac",
    "feature_desc" : " Montrac je dopravníkový systém s několika samostatnými vozíčky. Tyto vozíčky přepravují částečně zkompletované výrobky mezi několika stanicemi.",
    "background" : "Given line is on",
    "text_raw" : "scenario As soon as station XZX is free, then shuttle XY goes to station XZX.\nscenario As soon as robot R1 picks up cube 1, then robot R1 puts cube 1 on shuttle XY on position 1.\nscenario When station XXX is free and robot R1 finished unloading cube 3x2, then shuttle X goes to station XXX. \n scenario Given storage XYZ is empty, when robot R2 starts making product, then shuttle Y goes to station XXX",
    "language" : "en"
}


base_path = os.path.join(c.DATA_DIR, "input", "raw_out")

nl_to_signal(base_path, request)

nl_file_path = base_path + ".feature"
signal_file_path = base_path + "_signals.feature"

print("\n\n--- NL FILE ---")
with open(nl_file_path, "rt", encoding="utf-8") as f:
    text = f.read()
    print(text)

print("\n\n--- SIGNAL FILE ---")
with open(signal_file_path, "rt", encoding="utf-8") as f:
    text = f.read()
    print(text)