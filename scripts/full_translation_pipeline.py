import argparse
import subprocess
import os
import re

def run_command(command, description, cwd=None):
    print(f"\n--- {description} ---")
    print(f"Executando: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=False, cwd=cwd) # capture_output=False to show gst progress
        return result.returncode # Only return success/failure, stdout already printed
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}")
        # Standard error might be useful, but for gst we want output to console
        # print(f"Stderr: {e.stderr}") 
        raise
    except FileNotFoundError:
        print(f"Erro: O comando '{command[0]}' não foi encontrado. Certifique-se de que está instalado e no PATH.")
        raise

def full_translation_pipeline(video_file_path, target_language="Brazilian Portuguese", api_key=None):
    # Determine the directory of the current script (which is gemini-srt-translator)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # Parent directory is /home/marco/workspace/scripts/extract_sub/
    parent_dir = os.path.dirname(current_script_dir)

    # Define the output directory for all generated artifacts
    output_dir = os.path.join(current_script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Define paths for auxiliary scripts
    extract_sub_script_path = os.path.join(parent_dir, "extract_sub.sh")
    clean_dedup_srt_script_path = os.path.join(parent_dir, "clean_dedup_srt.py")
    reembed_srt_script_path = os.path.join(parent_dir, "reembed_srt.py")

    # Validate inputs
    video_file_path = os.path.abspath(video_file_path) # Ensure video_file_path is always absolute
    if not os.path.exists(video_file_path):
        print(f"Erro: O arquivo de vídeo '{video_file_path}' não foi encontrado.")
        return

    # Extract video basename and name without extension
    video_basename = os.path.basename(video_file_path)
    video_name_without_ext = os.path.splitext(video_basename)[0]
    video_ext = os.path.splitext(video_basename)[1]  # Preserva a extensão original (.mkv ou .mp4)

    # Define names for intermediate and final files, placing them in the output_dir
    extracted_srt_filename = f"{video_name_without_ext}.English.srt"
    extracted_srt_path_in_output = os.path.join(output_dir, extracted_srt_filename)
    # The extract_sub.sh script will output to the video's directory
    extracted_srt_path_in_video_dir = os.path.join(os.path.dirname(video_file_path), extracted_srt_filename)

    cleaned_srt_filename = f"{video_name_without_ext}.English.clean.srt"
    cleaned_srt_path = os.path.join(output_dir, cleaned_srt_filename)

    translated_srt_filename = f"{video_name_without_ext}.{target_language.replace(' ', '_').replace('(','').replace(')','').lower()}.clean_translated.srt"
    translated_srt_path = os.path.join(output_dir, translated_srt_filename)

    output_video_filename = f"{video_name_without_ext}_translated_{target_language.replace(' ', '_').replace('(','').replace(')','').lower()}{video_ext}"
    output_video_path = os.path.join(output_dir, output_video_filename)

    # 1. Extract subtitles
    # We run extract_sub.sh from parent_dir, but it outputs to video_file_path's directory
    run_command([extract_sub_script_path, video_file_path], "Extraindo legendas", cwd=parent_dir)

    # Move the extracted .srt from video's directory to output_dir
    if os.path.exists(extracted_srt_path_in_video_dir):
        os.rename(extracted_srt_path_in_video_dir, extracted_srt_path_in_output)
    else:
        print(f"Erro: Arquivo SRT extraído esperado em '{extracted_srt_path_in_video_dir}' não encontrado. "
              "Verifique o script 'extract_sub.sh' e o output.")
        return

    if not os.path.exists(extracted_srt_path_in_output):
        print(f"Erro: Arquivo SRT extraído esperado em '{extracted_srt_path_in_output}' não encontrado. "
              "Verifique o script 'extract_sub.sh' e o output.")
        return

    # 2. Clean and deduplicate SRT
    run_command(["python", clean_dedup_srt_script_path, extracted_srt_path_in_output], "Limpando e deduplicando legendas", cwd=parent_dir)
    if not os.path.exists(cleaned_srt_path):
        print(f"Erro: Arquivo SRT limpo esperado em '{cleaned_srt_path}' não encontrado.")
        return

    # 3. Translate SRT
    gst_command_args = ["gst", "translate", "-i", cleaned_srt_path, "-l", target_language, "-o", translated_srt_path]
    if api_key:
        gst_command_args.extend(["-k", api_key])
    
    run_command(gst_command_args, "Traduzindo legendas com Gemini SRT Translator", cwd=current_script_dir)
    if not os.path.exists(translated_srt_path):
        print(f"Erro: Arquivo SRT traduzido esperado em '{translated_srt_path}' não encontrado.")
        return

    # 4. Reembed translated SRT
    run_command([
        "python", reembed_srt_script_path,
        os.path.abspath(video_file_path),
        translated_srt_path,
        output_video_path,
        "--lang", "por", # Assuming "por" is Portuguese code
        "--default"
    ], "Reembutindo legenda traduzida no vídeo", cwd=parent_dir)

    print(f"\nProcesso concluído! Vídeo com legenda traduzida em: {output_video_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full pipeline to extract, clean, translate, and reembed subtitles for MKV and MP4 files.")
    parser.add_argument('video_file', help="Path to the input video file (MKV or MP4).")
    parser.add_argument('--lang', default="Brazilian Portuguese", help="Target language for translation. Default is 'Brazilian Portuguese'.")
    parser.add_argument('--api-key', help="Your Gemini API key. If not provided, assumes GEMINI_API_KEY environment variable is set.")

    args = parser.parse_args()

    full_translation_pipeline(os.path.abspath(args.video_file), args.lang, args.api_key)
