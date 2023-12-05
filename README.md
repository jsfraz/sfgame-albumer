# sfgame-albumer

Program pro automatické doplňování alba. Program funguje pro Steam verzi hry v okně s obrazovkou 1920x1080. Pro chod je vyžadován Svatý grál. Je doporučeno vypnout upozornění zpráv. Pokud nepoužíváte houby, spouštějte program pouze pokud není v aréně odpočet. Program také může dělat chyby a vyhodnocovat obraz špatně. Použití na vlastní nebezpečí.

## Kompilování

```
pip3 install -r requirements.txt
pyinstaller --name sfgame-albumer-v1.0.0 --windowed --icon icon.ico --onefile main.py
```
