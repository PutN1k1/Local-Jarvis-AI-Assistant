text = """руби следщу;next_track
следущий трек;next_track
скипн трек;next_track
переключи;next_track
трекк следующий;next_track
следуцкий трек;next_track
давай следущий;next_track
дропн следующий;next_track
скипп;next_track
следую трек;next_track
ну эээ кринж скипни;next_track
алё голова счас лопнет от басов;next_track
короче го на следующий;next_track
скип типа это не то;next_track
эээ дропни новый трек;next_track"""

with open('C:\\PythonProjects\\Local Jarvis ( AI Assistant )\\model train\\mega_dataset_5k.csv', 'w', encoding='utf-8') as f:
    try:
        
        f.write(text + "\n")
        print("writed")
    except Exception as e:
        print(f"Ошибка: {e}")