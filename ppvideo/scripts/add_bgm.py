import argparse
from moviepy import VideoFileClip, AudioFileClip
import moviepy.audio.fx as afx
import os
from datetime import datetime

def add_bgm(video_path, bgm_path, output_path, volume=0.3):
    # 加载视频
    video_clip = VideoFileClip(video_path)

    # 加载并裁剪音频（避免过长问题）
    bgm_clip = (
        AudioFileClip(bgm_path)
        .subclipped(0, video_clip.duration)
        .with_effects([
            afx.MultiplyVolume(volume),
            afx.AudioFadeOut(3),
        ])
    )

    # 合成音频
    final_video = video_clip.with_audio(bgm_clip)

    # 输出视频
    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac"
    )


def main():
    parser = argparse.ArgumentParser(description="Add BGM to video using MoviePy")
    parser.add_argument("video", help="Input video file (e.g. input.mp4)")
    parser.add_argument("bgm", help="Background music file (mp3/mp4)")
    parser.add_argument("-o", "--output", help="Output file name (optional)")
    parser.add_argument("-v", "--volume", type=float, default=0.3, help="BGM volume (default 0.3)")

    args = parser.parse_args()
    
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        video_name = os.path.splitext(os.path.basename(args.video))[0]
        output_path = f"{video_name}_with_bgm_{timestamp}.mp4"

    #print(f"Output file: {output_path}")
    add_bgm(args.video, args.bgm, output_path, args.volume)


if __name__ == "__main__":
    main()
