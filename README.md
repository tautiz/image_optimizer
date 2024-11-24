# Image Optimizer

Įrankis nuotraukų optimizavimui interneto svetainėms. Automatiškai sumažina nuotraukų dydį ir optimizuoja jų kokybę.

## Įdiegimas

```bash
pip install .
```

## Naudojimas

```bash
# Apdoroti visus ZIP failus esamame kataloge
imgoptimize

# Apdoroti konkretų ZIP failą
imgoptimize kelias/iki/failo.zip

# Nurodyti kokybę ir maksimalų dydį
imgoptimize --quality 75 --max-size 1600

# Apdoroti katalogą
imgoptimize kelias/iki/katalogo
```

## Parametrai

- `input_path`: Kelias iki nuotraukų katalogo arba ZIP failo (neprivaloma)
- `--output-dir`: Katalogas optimizuotoms nuotraukoms (pagal nutylėjimą: šalia įvesties failo)
- `--max-size`: Maksimalus nuotraukos kraštinės ilgis (pagal nutylėjimą: 1920px)
- `--quality`: JPEG kokybė 0-100 (pagal nutylėjimą: 85)
