import argparse
import subprocess
import os

def reembed_srt(video_file, srt_file, output_file, language='por', default_track=True):
    """
    Reembeds an SRT subtitle file into an MKV video file.

    Args:
        video_file (str): Path to the input MKV video file.
        srt_file (str): Path to the SRT subtitle file to embed.
        output_file (str): Path for the output MKV video file.
        language (str): Language code for the subtitle track (e.g., 'por' for Portuguese, 'eng' for English).
        default_track (bool): Set the new subtitle track as default (True) or not (False).
    """
    if not os.path.exists(video_file):
        print(f"Erro: O arquivo de vídeo '{video_file}' não foi encontrado.")
        return

    if not os.path.exists(srt_file):
        print(f"Erro: O arquivo SRT '{srt_file}' não foi encontrado.")
        return

    # Comando básico para adicionar a legenda
    command = [
        'mkvmerge', '-o', output_file, video_file,
        '--language', f'0:{language}',
    ]

    # Adiciona a flag --default-track se for para ser a faixa padrão
    if default_track:
        command.extend(['--default-track', '0'])
    
    command.append(srt_file)

    print(f"Executando comando: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Legenda '{srt_file}' reembutida com sucesso em '{output_file}'.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao reembutir legenda: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print("Erro: 'mkvmerge' não encontrado. Certifique-se de que o mkvtoolnix está instalado e no PATH.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reembeds an SRT subtitle file into an MKV video file using mkvmerge.")
    parser.add_argument('video_file', help="Path to the input MKV video file.")
    parser.add_argument('srt_file', help="Path to the SRT subtitle file to embed.")
    parser.add_argument('output_file', help="Path for the output MKV video file.")
    parser.add_argument('--lang', default='por', help="Language code for the subtitle track (e.g., 'por', 'eng'). Default is 'por'.")
    parser.add_argument('--default', action='store_true', help="Set the new subtitle track as default.")

    args = parser.parse_args()

    reembed_srt(args.video_file, args.srt_file, args.output_file, language=args.lang, default_track=args.default)
