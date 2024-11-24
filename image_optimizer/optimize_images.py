import os
from PIL import Image
import argparse
from pathlib import Path
import zipfile
import tempfile
import shutil
import glob

# Numatytosios reikšmės
DEFAULT_MAX_SIZE = 1920  # maksimalus kraštinės ilgis pikseliais
DEFAULT_QUALITY = 85     # JPEG kokybė (0-100)

def optimize_image(input_path: Path, output_path: Path, max_size: int = DEFAULT_MAX_SIZE, quality: int = DEFAULT_QUALITY):
    """
    Optimizuoja nuotrauką sumažindama jos dydį ir kokybę.
    
    :param input_path: Kelias iki originalios nuotraukos
    :param output_path: Kelias, kur išsaugoti optimizuotą nuotrauką
    :param max_size: Maksimalus nuotraukos kraštinės ilgis pikseliais
    :param quality: JPEG kokybės parametras (0-100)
    """
    try:
        # Atidarome nuotrauką
        with Image.open(input_path) as img:
            # Konvertuojame į RGB (jei reikia)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Gauname originalius matmenis
            width, height = img.size
            
            # Skaičiuojame naujus matmenis išlaikant proporcijas
            if width > max_size or height > max_size:
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                
                # Keičiame nuotraukos dydį
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Sukuriame output katalogą, jei jo nėra
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Išsaugome optimizuotą nuotrauką
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            # Skaičiuojame sutaupytą vietą
            original_size = os.path.getsize(input_path)
            optimized_size = os.path.getsize(output_path)
            saved = original_size - optimized_size
            
            print(f"Optimizuota: {input_path.name}")
            print(f"Sutaupyta: {saved / 1024:.1f} KB ({(saved / original_size * 100):.1f}%)")
            
            return saved
            
    except Exception as e:
        print(f"Klaida apdorojant {input_path.name}: {str(e)}")
        return 0

def process_directory(input_dir: Path, output_dir: Path, max_size: int = DEFAULT_MAX_SIZE, quality: int = DEFAULT_QUALITY):
    """
    Apdoroja visas nuotraukas kataloge
    """
    image_extensions = ('.jpg', '.jpeg', '.png')
    total_saved = 0
    total_files = 0
    
    for file_path in input_dir.rglob('*'):
        if file_path.suffix.lower() in image_extensions:
            relative_path = file_path.relative_to(input_dir)
            output_path = output_dir / relative_path.with_suffix('.jpg')
            
            saved = optimize_image(file_path, output_path, max_size, quality)
            total_saved += saved
            total_files += 1
    
    return total_files, total_saved

def process_zip(zip_path: Path, output_dir: Path, max_size: int = DEFAULT_MAX_SIZE, quality: int = DEFAULT_QUALITY):
    """
    Apdoroja nuotraukas iš ZIP failo
    """
    # Sukuriame laikiną katalogą išpakuotiems failams
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Išpakuojame ZIP failą
        print(f"\nIšpakuojamas ZIP failas: {zip_path.name}")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            # Apdorojame išpakuotas nuotraukas
            return process_directory(temp_path, output_dir, max_size, quality)
        except Exception as e:
            print(f"Klaida apdorojant ZIP failą {zip_path.name}: {str(e)}")
            return 0, 0

def process_all_zips(directory: Path, max_size: int = DEFAULT_MAX_SIZE, quality: int = DEFAULT_QUALITY):
    """
    Apdoroja visus ZIP failus nurodytame kataloge
    """
    total_files = 0
    total_saved = 0
    zip_count = 0
    
    # Ieškome visų ZIP failų
    for zip_path in directory.glob('*.zip'):
        zip_count += 1
        # Sukuriame išvesties katalogą pagal ZIP failo pavadinimą
        output_dir = zip_path.parent / zip_path.stem
        
        # Apdorojame ZIP failą
        files, saved = process_zip(zip_path, output_dir, max_size, quality)
        total_files += files
        total_saved += saved
    
    return zip_count, total_files, total_saved

def main():
    parser = argparse.ArgumentParser(description='Nuotraukų optimizavimas interneto svetainei')
    parser.add_argument('input_path', nargs='?', 
                      help='Kelias iki nuotraukų katalogo arba ZIP failo (neprivaloma)', 
                      type=str)
    parser.add_argument('--output-dir', 
                      help='Katalogas optimizuotoms nuotraukoms (pagal nutylėjimą: šalia įvesties failo)', 
                      type=str)
    parser.add_argument('--max-size', 
                      type=int, 
                      help=f'Maksimalus nuotraukos kraštinės ilgis (pagal nutylėjimą: {DEFAULT_MAX_SIZE}px)', 
                      default=DEFAULT_MAX_SIZE)
    parser.add_argument('--quality', 
                      type=int, 
                      help=f'JPEG kokybė 0-100 (pagal nutylėjimą: {DEFAULT_QUALITY})', 
                      default=DEFAULT_QUALITY)
    
    args = parser.parse_args()
    
    # Patikriname quality reikšmę
    if args.quality < 0 or args.quality > 100:
        print(f"Klaida: kokybė turi būti tarp 0 ir 100 (nurodyta: {args.quality})")
        return
    
    # Patikriname max_size reikšmę
    if args.max_size < 100:
        print(f"Klaida: max-size negali būti mažesnis nei 100px (nurodyta: {args.max_size})")
        return
    
    if args.input_path:
        # Pašaliname escape charakterius iš kelių
        input_path = Path(args.input_path.replace('\\', ''))
        
        # Jei output_dir nenurodyta, naudojame input failo pavadinimą be plėtinio
        if args.output_dir:
            output_dir = Path(args.output_dir.replace('\\', ''))
        else:
            if input_path.is_file() and input_path.suffix.lower() == '.zip':
                output_dir = input_path.parent / input_path.stem
            else:
                output_dir = input_path.parent / (input_path.name + '_optimized')
        
        if not input_path.exists():
            print(f"Klaida: {input_path} neegzistuoja!")
            return
        
        # Apdorojame ZIP failą arba katalogą
        if input_path.is_file() and input_path.suffix.lower() == '.zip':
            total_files, total_saved = process_zip(input_path, output_dir, args.max_size, args.quality)
            zip_count = 1
        else:
            total_files, total_saved = process_directory(input_path, output_dir, args.max_size, args.quality)
            zip_count = 0
    else:
        # Jei kelias nenurodytas, apdorojame visus ZIP failus esamame kataloge
        current_dir = Path.cwd()
        print(f"Ieškoma ZIP failų kataloge: {current_dir}")
        zip_count, total_files, total_saved = process_all_zips(current_dir, args.max_size, args.quality)
    
    # Spausdiname rezultatus
    if total_files > 0:
        print(f"\nOptimizavimas baigtas!")
        print(f"Naudoti parametrai:")
        print(f"- Maksimalus kraštinės ilgis: {args.max_size}px")
        print(f"- JPEG kokybė: {args.quality}")
        if zip_count > 0:
            print(f"Apdorota ZIP failų: {zip_count}")
        print(f"Apdorota nuotraukų: {total_files}")
        print(f"Iš viso sutaupyta: {total_saved / 1024 / 1024:.1f} MB")
    else:
        if zip_count == 0:
            print("Nerasta ZIP failų apdorojimui!")
        else:
            print("Nerasta tinkamų nuotraukų apdorojimui ZIP failuose!")

if __name__ == '__main__':
    main()
