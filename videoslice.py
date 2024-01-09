import os
import random
from moviepy.editor import VideoFileClip, clips_array, concatenate_videoclips

SUPPORTED_EXTENSIONS = {'.mp4', '.mov', '.avi'}

def slice_video(input_path, height=100):
    clip = VideoFileClip(input_path)
    total_duration = clip.duration
    num_slices = int(clip.size[1] / height)

    slices = []
    for i in range(num_slices):
        start_time = i * total_duration / num_slices
        end_time = (i + 1) * total_duration / num_slices
        slice_clip = clip.subclip(start_time, end_time)
        slice_clip = slice_clip.crop(y1=i * height, y2=(i + 1) * height)
        # slice_clip = slice_clip.resize(height=height)
        slices.append(slice_clip)

    return slices

def process_videos(input_directory, slices_high, max_files=10, height=100):
    input_files = [f for f in os.listdir(input_directory) if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS]
    random.shuffle(input_files)
    selected_files = input_files[:max_files]

    all_slices = []
    max_duration = 0

    for file in selected_files:
        input_path = os.path.join(input_directory, file)
        slices = slice_video(input_path, height)
        all_slices.extend(slices)
        max_duration = max(max_duration, sum(clip.duration for clip in slices))

    final_slices = []
    for slice_clip in all_slices:
        repetitions = int(max_duration / slice_clip.duration)
        repeated_clip = concatenate_videoclips([slice_clip] * repetitions)
        final_slices.append(repeated_clip)

    selected_slices = random.sample(final_slices, min(slices_high, len(selected_files)))

    final_video = clips_array([[clip] for clip in selected_slices], bg_color=(0, 0, 0))
    final_video.write_videofile('output.mp4', codec='h264_videotoolbox', fps=24)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Video Slicer and Assembler')
    parser.add_argument('--input', default='source', help='Input directory containing video files')
    parser.add_argument('--slicesHigh', type=int, default=10, help='Number of slices high in the final video')
    parser.add_argument('--maxFiles', type=int, default=10, help='Maximum number of videos to process')
    parser.add_argument('--height', type=int, default=100, help='Height of each slice')

    args = parser.parse_args()

    process_videos(args.input, args.slicesHigh, args.maxFiles, args.height)
