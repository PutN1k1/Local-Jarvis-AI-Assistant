import pymorphy3
morph = pymorphy3.MorphAnalyzer()
p = morph.parse("Никиты")[0]
print(p.normal_form)