import argparse
import glob
import os
from moviepy import ImageClip, concatenate_videoclips


def expand_images(image_patterns):
    images = []
    for pattern in image_patterns:
        matched = glob.glob(pattern)
        if matched:
            images.extend(sorted(matched))
        else:
            images.append(pattern)
    return images


def create_video(images, duration, output, fps):
    clips = [ImageClip(img).with_duration(duration) for img in images]
    video = concatenate_videoclips(clips)

    video.write_videofile(
        output,
        fps=fps,
        codec="libx264",
        audio=False,
        ffmpeg_params=[
            "-pix_fmt", "yuv420p",
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2"
        ]
    )


def cleanup_files(images):
    for img in images:
        if os.path.exists(img):
            #print(f"Removing {img}")
            os.remove(img)


def main():
    parser = argparse.ArgumentParser(
        description="Create a video slideshow from images"
    )

    parser.add_argument("images", nargs="+", help="Image files or patterns")
    parser.add_argument("-d", "--duration", type=float, default=3)
    parser.add_argument("-o", "--output", default="slides.mp4")
    parser.add_argument("--fps", type=int, default=24)

    # 👇 important safety flag
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete input images after video creation"
    )

    args = parser.parse_args()

    images = expand_images(args.images)

    if not images:
        raise ValueError("No images found!")

    print("Using images:", images)

    # 👇 only cleanup if success
    try:
        create_video(images, args.duration, args.output, args.fps)
    except Exception as e:
        print("Error during video creation:", e)
        return

    if args.cleanup:
        cleanup_files(images)


if __name__ == "__main__":
    main()
