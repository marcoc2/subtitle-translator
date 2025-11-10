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

    if output_ext == '.mkv':
        # Usa mkvmerge para MKV
        command = [
            'mkvmerge', '-o', output_file, video_file,
            '--language', f'0:{language}',
        ]

        # Adiciona a flag --default-track se for para ser a faixa padrão
        if default_track:
            command.extend(['--default-track', '0'])

        command.append(srt_file)

        print(f"Executando comando (mkvmerge): {' '.join(command)}")
        try:
            subprocess.run(command, check=True, text=True, capture_output=True)
            print(f"Legenda '{srt_file}' reembutida com sucesso em '{output_file}'.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao reembutir legenda: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
        except FileNotFoundError:
            print("Erro: 'mkvmerge' não encontrado. Certifique-se de que o mkvtoolnix está instalado e no PATH.")

    elif output_ext == '.mp4':
        # Usa FFmpeg para MP4
        # FFmpeg copia os streams de vídeo e áudio, e adiciona a legenda como nova stream
        command = [
            'ffmpeg', '-y',  # -y sobrescreve arquivo de saída se existir
            '-i', video_file,
            '-i', srt_file,
            '-c', 'copy',  # Copia streams sem recodificar (mais rápido)
            '-c:s', 'mov_text',  # Codec de legenda para MP4
            '-metadata:s:s:0', f'language={language}',
        ]

        # Para MP4, o conceito de "default" é diferente, mas podemos marcar com disposition
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

    else:
        print(f"Erro: Formato de saída '{output_ext}' não suportado. Use .mkv ou .mp4")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reembeds an SRT subtitle file into a video file (MKV or MP4).")
    parser.add_argument('video_file', help="Path to the input video file (MKV or MP4).")
    parser.add_argument('srt_file', help="Path to the SRT subtitle file to embed.")
    parser.add_argument('output_file', help="Path for the output video file (MKV or MP4).")
    parser.add_argument('--lang', default='por', help="Language code for the subtitle track (e.g., 'por', 'eng'). Default is 'por'.")
    parser.add_argument('--default', action='store_true', help="Set the new subtitle track as default.")

    args = parser.parse_args()

    reembed_srt(args.video_file, args.srt_file, args.output_file, language=args.lang, default_track=args.default)
