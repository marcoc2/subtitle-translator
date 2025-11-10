import argparse
import subprocess
import os

def reembed_srt(video_file, srt_file, output_file, language='por', default_track=True):
    """
    Reembeds an SRT subtitle file into a video file (MKV or MP4).

    Args:
        video_file (str): Path to the input video file (MKV or MP4).
        srt_file (str): Path to the SRT subtitle file to embed.
        output_file (str): Path for the output video file.
        language (str): Language code for the subtitle track (e.g., 'por' for Portuguese, 'eng' for English).
        default_track (bool): Set the new subtitle track as default (True) or not (False).
    """
    if not os.path.exists(video_file):
        print(f"Erro: O arquivo de vídeo '{video_file}' não foi encontrado.")
        return

    if not os.path.exists(srt_file):
        print(f"Erro: O arquivo SRT '{srt_file}' não foi encontrado.")
        return

    # Detecta o formato de saída pela extensão
    output_ext = os.path.splitext(output_file)[1].lower()

    if output_ext not in ['.mkv', '.mp4']:
        print(f"Erro: Formato de saída '{output_ext}' não suportado. Use .mkv ou .mp4")
        return

    # Usa FFmpeg para ambos os formatos (MKV e MP4)
    # Constrói o comando base
    command = [
        'ffmpeg', '-y',  # -y sobrescreve arquivo de saída se existir
        '-i', video_file,
        '-i', srt_file,
        '-c', 'copy',  # Copia streams de vídeo/áudio sem recodificar (mais rápido)
    ]

    # Define o codec de legenda apropriado para cada formato
    if output_ext == '.mkv':
        command.extend(['-c:s', 'srt'])  # Codec de legenda para MKV
    elif output_ext == '.mp4':
        command.extend(['-c:s', 'mov_text'])  # Codec de legenda para MP4

    # Adiciona metadados de idioma
    command.extend(['-metadata:s:s:0', f'language={language}'])

    # Define a legenda como padrão se solicitado
    if default_track:
        command.extend(['-disposition:s:0', 'default'])

    command.append(output_file)

    print(f"Executando comando (ffmpeg): {' '.join(command)}")
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Legenda '{srt_file}' reembutida com sucesso em '{output_file}'.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao reembutir legenda: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print("Erro: 'ffmpeg' não encontrado. Certifique-se de que o FFmpeg está instalado e no PATH.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reembeds an SRT subtitle file into a video file (MKV or MP4).")
    parser.add_argument('video_file', help="Path to the input video file (MKV or MP4).")
    parser.add_argument('srt_file', help="Path to the SRT subtitle file to embed.")
    parser.add_argument('output_file', help="Path for the output video file (MKV or MP4).")
    parser.add_argument('--lang', default='por', help="Language code for the subtitle track (e.g., 'por', 'eng'). Default is 'por'.")
    parser.add_argument('--default', action='store_true', help="Set the new subtitle track as default.")

    args = parser.parse_args()

    reembed_srt(args.video_file, args.srt_file, args.output_file, language=args.lang, default_track=args.default)
