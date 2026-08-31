from celery import shared_task
import os
import subprocess
from django.conf import settings
from django.core.files import File
import logging
from .models import Lesson, UserLessonStatus
from django.contrib.auth import get_user_model
import shutil
logger = logging.getLogger(__name__)

# @shared_task
# def generate_watermarked_video_task_fast(video_path, user_id, lesson_id):
#     logger = logging.getLogger(__name__)

#     try:
#         User = get_user_model()
#         user_main = User.objects.get(id=user_id)
#         logger.info(f"User retrieved: {user_main}")

#         lesson = Lesson.objects.filter(id=lesson_id).first()
#         if not lesson:
#             logger.error(f"No lesson found for video_path: {video_path}")
#             return None

#         userLesson, created = UserLessonStatus.objects.get_or_create(
#             user=user_main,
#             lesson=lesson,
#         )

#         userLesson.watermarked_video = lesson.video
#         userLesson.save()

#         logger.info(f"UserLessonStatus updated with video path (no copy): {userLesson.watermarked_video.url}")
#         return lesson.video.url

#     except Exception as e:
#         logger.error(f"Error updating UserLessonStatus with original video: {str(e)}")
#         return str(e)


@shared_task
def generate_watermarked_video_task_fast(video_path, user_id, lesson_id):


    logger = logging.getLogger(__name__)

    try:
        User = get_user_model()
        user_main = User.objects.get(id=user_id)
        logger.info(f"User retrieved: {user_main}")

        lesson = Lesson.objects.filter(id=lesson_id).first()
        if not lesson:
            logger.error(f"No lesson found for video_path: {video_path}")
            return None

        userLesson, created = UserLessonStatus.objects.get_or_create(
            user=user_main,
            lesson=lesson,
        )

        output_filename = os.path.basename(video_path)  
        output_dir = os.path.join(settings.MEDIA_ROOT, 'watermarked_videos')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        shutil.copyfile(video_path, output_path)

        with open(output_path, 'rb') as f:
            userLesson.watermarked_video.save(output_filename, File(f))
            userLesson.save()

        logger.info(f"UserLessonStatus updated with original video: {userLesson.watermarked_video}")
        return lesson.video.url

    except Exception as e:
        logger.error(f"Error updating UserLessonStatus with original video: {str(e)}")
        return str(e)
def generate_watermarked_video(
    video_path,
    watermark_text,
    font_path,
    output_path,
    font_size=100,
    font_color="#CC5500",
    box_color="black@0.5",
    box_border_width=5,
    threads=8,
    thread_type="slice",
    video_codec="libx264",
    overwrite=True,
):
    """
    Generate a watermarked video using FFmpeg.

    Args:
        video_path (str): Path to the input video.
        watermark_text (str): Text to use as the watermark.
        font_path (str): Path to the font file.
        output_path (str): Path to save the output video.
        font_size (int): Font size of the watermark text.
        font_color (str): Color of the watermark text.
        box_color (str): Background color of the watermark box.
        box_border_width (int): Border width of the watermark box.
        threads (int): Number of threads to use for encoding.
        thread_type (str): Threading model (e.g., "slice").
        video_codec (str): Video codec to use (e.g., "libx264", "h264_nvenc").
        overwrite (bool): Whether to overwrite the output file if it exists.

    Returns:
        bool: True if successful, False otherwise.
    """
    return True
    # try:
    #     # FFmpeg command to add watermark
    #     ffmpeg_command = [
    #         'ffmpeg',
    #         '-i', video_path,  # Input video
    #         '-vf', f"drawtext=text='{watermark_text}':fontfile={font_path}:fontsize={font_size}:fontcolor={font_color}:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor={box_color}:boxborderw={box_border_width}",
    #         '-c:v', video_codec,  # Video codec
    #         '-c:a', 'copy',  # Copy audio stream without re-encoding
    #         # '-preset', preset,  # Encoding speed preset
    #         '-threads', str(threads),  # Number of threads
    #         '-thread_type', thread_type,  # Threading model
    #         '-y' if overwrite else '-n',  # Overwrite output file if it exists
    #         output_path
    #     ]

    #     # Run the FFmpeg command
    #     subprocess.run(ffmpeg_command, check=True)
    #     return True
    # except subprocess.CalledProcessError as e:
    #     logger.error(f"FFmpeg command failed: {e}")
    #     return False
    # except Exception as e:
    #     logger.error(f"Error generating watermarked video: {e}")
    #     return False


@shared_task
def generate_watermarked_video_task(video_path, user_first_name, user_last_name, user_phone_number, user_id, course_id):
    font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'Arial.ttf')
    logger.info(f"generate_watermarked_video_task")

    try:
        User = get_user_model()
        user_main = User.objects.get(id=user_id)
        logger.info(f"User retrieved: {user_main}")

        # Find the lesson associated with the video
        lesson = Lesson.objects.filter(course_id=course_id).first()
        if not lesson:
            logger.error(f"No lesson found for video_path: {video_path}")
            return None
        logger.info(f"Lesson retrieved: {lesson}")

        # Create or retrieve UserLessonStatus
        userLesson, created = UserLessonStatus.objects.get_or_create(
            user=user_main,
            lesson=lesson,
            defaults={
                # Add any default fields here if needed
            }
        )
        logger.info(f"UserLessonStatus retrieved or created: {userLesson}, created: {created}")

        # Watermark text
        watermark_text = f"{user_main.username} - {user_phone_number}"

        # Output file path
        output_filename = f"watermarked_{os.path.basename(video_path)}"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'watermarked_videos')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        # Generate the watermarked video
        success = generate_watermarked_video(
            video_path=video_path,
            watermark_text=watermark_text,
            font_path=font_path,
            output_path=output_path,
            font_size=100,  # Adjust as needed
            font_color="#CC5500",  # Adjust as needed
            box_color="black@0.5",  # Adjust as needed
            box_border_width=5,  # Adjust as needed
            threads=8,  # Adjust based on CPU cores
            thread_type="slice",  # Adjust threading model
            video_codec="libx264",  # Use "h264_nvenc" for NVIDIA GPUs
            overwrite=True,  # Overwrite output file if it exists
        )

        if not success:
            raise Exception("Failed to generate watermarked video")

        # Save the watermarked video to the UserLessonStatus model
        with open(output_path, 'rb') as f:
            userLesson.watermarked_video.save(output_filename, File(f))
            userLesson.save()

        logger.info(f"generate_watermarked_video_task lesson.video.url {userLesson.watermarked_video}")
        return lesson.video.url if lesson else None

    except Exception as e:
        logger.error(f"Error generating watermarked video: {str(e)}")
        return str(e)



def reduce_video_size(input_path, output_path, crf=26, video_codec="libx265", audio_codec="aac", audio_bitrate="128k"):
    """
    Reduce the size of a video without significant quality loss using FFmpeg.

    Args:
        input_path (str): Path to the input video file.
        output_path (str): Path to save the output video file.
        crf (int): Constant Rate Factor (lower = better quality, higher = smaller file size).
                   Recommended: 23-28 for H.265.
        video_codec (str): Video codec to use (e.g., "libx265" for H.265, "libx264" for H.264).
        audio_codec (str): Audio codec to use (e.g., "aac").
        audio_bitrate (str): Audio bitrate (e.g., "128k").

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # FFmpeg command to reduce video size
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_path,  # Input video
            '-c:v', video_codec,  # Video codec
            '-crf', str(crf),  # Constant Rate Factor
            '-c:a', audio_codec,  # Audio codec
            '-b:a', audio_bitrate,  # Audio bitrate
            '-y',  # Overwrite output file if it exists
            output_path
        ]

        # Run the FFmpeg command
        subprocess.run(ffmpeg_command, check=True)
        logger.info(f"Video size reduced successfully: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg command failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Error reducing video size: {e}")
        return False


@shared_task
def reduce_video_size_task(video_path, user_id, course_id):
    logger.info(f"reduce_video_size_task")

    try:
        User = get_user_model()
        user_main = User.objects.get(id=user_id)
        logger.info(f"User retrieved: {user_main}")

        # Find the lesson associated with the video
        lesson = Lesson.objects.filter(course_id=course_id).first()
        if not lesson:
            logger.error(f"No lesson found for video_path: {video_path}")
            return None
        logger.info(f"Lesson retrieved: {lesson}")

        # Create or retrieve UserLessonStatus
        userLesson, created = UserLessonStatus.objects.get_or_create(
            user=user_main,
            lesson=lesson,
            defaults={
                # Add any default fields here if needed
            }
        )
        logger.info(f"UserLessonStatus retrieved or created: {userLesson}, created: {created}")

        # Output file path
        output_filename = f"reduced_{os.path.basename(video_path)}"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'watermarked_videos')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        # Reduce the video size
        success = reduce_video_size(
            input_path=video_path,
            output_path=output_path,
            crf=26,  # Adjust CRF for quality (23-28 for H.265)
            video_codec="libx265",  # Use H.265 for better compression
            audio_codec="aac",  # Use AAC for audio
            audio_bitrate="128k",  # Set audio bitrate
        )

        if not success:
            raise Exception("Failed to reduce video size")

        # Save the reduced video to the UserLessonStatus model
        with open(output_path, 'rb') as f:
            userLesson.watermarked_video.save(output_filename, File(f))
            userLesson.save()

        logger.info(f"reduce_video_size_task lesson.video.url {userLesson.watermarked_video}")
        return lesson.video.url if lesson else None

    except Exception as e:
        logger.error(f"Error reducing video size: {str(e)}")
        return str(e)


def reduce_video_size_fast(input_path, output_path, crf=26, preset="veryfast", video_codec="libx264", audio_codec="aac", audio_bitrate="128k", resize=None):
    """
    Reduce the size of a video quickly using FFmpeg.

    Args:
        input_path (str): Path to the input video file.
        output_path (str): Path to save the output video file.
        crf (int): Constant Rate Factor (lower = better quality, higher = smaller file size).
                   Recommended: 23-28 for H.264.
        preset (str): Encoding speed preset (e.g., "ultrafast", "superfast", "veryfast").
        video_codec (str): Video codec to use (e.g., "libx264" for H.264, "libx265" for H.265).
        audio_codec (str): Audio codec to use (e.g., "aac").
        audio_bitrate (str): Audio bitrate (e.g., "128k").
        resize (tuple): Optional. Resize the video to (width, height). Example: (1280, 720).

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Base FFmpeg command
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_path,  # Input video
            '-c:v', video_codec,  # Video codec
            '-crf', str(crf),  # Constant Rate Factor
            '-preset', preset,  # Encoding speed preset
            '-c:a', audio_codec,  # Audio codec
            '-b:a', audio_bitrate,  # Audio bitrate
            '-y',  # Overwrite output file if it exists
        ]

        # Add resize filter if specified
        if resize:
            ffmpeg_command.extend(['-vf', f'scale={resize[0]}:{resize[1]}'])

        # Add output path
        ffmpeg_command.append(output_path)

        # Run the FFmpeg command
        subprocess.run(ffmpeg_command, check=True)
        logger.info(f"Video size reduced successfully: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg command failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Error reducing video size: {e}")
        return False


@shared_task
def reduce_video_size_task_fast(video_path, user_id, course_id):
    logger.info(f"reduce_video_size_task")

    try:
        User = get_user_model()
        user_main = User.objects.get(id=user_id)
        logger.info(f"User retrieved: {user_main}")

        # Find the lesson associated with the video
        lesson = Lesson.objects.filter(course_id=course_id).first()
        if not lesson:
            logger.error(f"No lesson found for video_path: {video_path}")
            return None
        logger.info(f"Lesson retrieved: {lesson}")

        # Create or retrieve UserLessonStatus
        userLesson, created = UserLessonStatus.objects.get_or_create(
            user=user_main,
            lesson=lesson,
            defaults={
                # Add any default fields here if needed
            }
        )
        logger.info(f"UserLessonStatus retrieved or created: {userLesson}, created: {created}")

        # Output file path
        output_filename = f"reduced_{os.path.basename(video_path)}"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'watermarked_videos')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        # Reduce the video size quickly
        success = reduce_video_size_fast(
            input_path=video_path,
            output_path=output_path,
            crf=26,  # Adjust CRF for quality (23-28 for H.264)
            preset="veryfast",  # Use a faster preset
            video_codec="libx264",  # Use H.264 for faster encoding
            audio_codec="aac",  # Use AAC for audio
            audio_bitrate="128k",  # Set audio bitrate
            resize=(1280, 720),  # Optional: Resize to 720p for faster encoding
        )

        if not success:
            raise Exception("Failed to reduce video size")

        # Save the reduced video to the UserLessonStatus model
        with open(output_path, 'rb') as f:
            userLesson.watermarked_video.save(output_filename, File(f))
            userLesson.save()

        logger.info(f"reduce_video_size_task lesson.video.url {userLesson.watermarked_video}")
        return lesson.video.url if lesson else None

    except Exception as e:
        logger.error(f"Error reducing video size: {str(e)}")
        return str(e)


    font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'Arial.ttf')
    logger.info(f"generate_watermarked_video_task_fast")

    try:
        User = get_user_model()
        user_main = User.objects.get(id=user_id)
        logger.info(f"User retrieved: {user_main}")

        # Find the lesson associated with the video
        lesson = Lesson.objects.filter(course_id=course_id).first()
        if not lesson:
            logger.error(f"No lesson found for video_path: {video_path}")
            return None
        logger.info(f"Lesson retrieved: {lesson}")

        # Create or retrieve UserLessonStatus
        userLesson, created = UserLessonStatus.objects.get_or_create(
            user=user_main,
            lesson=lesson,
            defaults={
                # Add any default fields here if needed
            }
        )
        logger.info(f"UserLessonStatus retrieved or created: {userLesson}, created: {created}")

        # Watermark text
        watermark_text = f"{user_main.username} - {user_phone_number}"

        # Output file path
        output_filename = f"watermarked_{os.path.basename(video_path)}"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'watermarked_videos')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        # Generate the watermarked video quickly
        success = generate_watermarked_video_fast(
            input_path=video_path,
            watermark_text=watermark_text,
            font_path=font_path,
            output_path=output_path,
            font_size=100,  # Adjust as needed
            font_color="#CC5500",  # Adjust as needed
            box_color="black@0.5",  # Adjust as needed
            box_border_width=5,  # Adjust as needed
            threads=8,  # Use 8 threads for encoding
            preset="veryfast",  # Use a faster preset
            video_codec="libx264",  # Use H.264 for faster encoding
        )

        if not success:
            raise Exception("Failed to generate watermarked video")

        # Save the watermarked video to the UserLessonStatus model
        with open(output_path, 'rb') as f:
            userLesson.watermarked_video.save(output_filename, File(f))
            userLesson.save()

        logger.info(f"generate_watermarked_video_task_fast lesson.video.url {userLesson.watermarked_video}")
        return lesson.video.url if lesson else None

    except Exception as e:
        logger.error(f"Error generating watermarked video: {str(e)}")
        return str(e)
    font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'Arial.ttf')
    logger.info(f"generate_watermarked_video_task_fast")

    try:
        User = get_user_model()
        user_main = User.objects.get(id=user_id)
        logger.info(f"User retrieved: {user_main}")

        # Find the lesson associated with the video
        lesson = Lesson.objects.filter(course_id=course_id).first()
        if not lesson:
            logger.error(f"No lesson found for video_path: {video_path}")
            return None
        logger.info(f"Lesson retrieved: {lesson}")

        # Create or retrieve UserLessonStatus
        userLesson, created = UserLessonStatus.objects.get_or_create(
            user=user_main,
            lesson=lesson,
            defaults={
                # Add any default fields here if needed
            }
        )
        logger.info(f"UserLessonStatus retrieved or created: {userLesson}, created: {created}")

        # Watermark text
        watermark_text = f"{user_main.username} - {user_phone_number}"

        # Output file path
        output_filename = f"watermarked_{os.path.basename(video_path)}"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'watermarked_videos')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        # Generate the watermarked video quickly
        success = generate_watermarked_video_fast(
            input_path=video_path,
            watermark_text=watermark_text,
            font_path=font_path,
            output_path=output_path,
            font_size=100,  # Adjust as needed
            font_color="#CC5500",  # Adjust as needed
            box_color="black@0.5",  # Adjust as needed
            box_border_width=5,  # Adjust as needed
            threads=8,  # Use 8 threads for encoding
            preset="veryfast",  # Use a faster preset
            video_codec="libx264",  # Use H.264 for faster encoding
        )

        if not success:
            raise Exception("Failed to generate watermarked video")

        # Save the watermarked video to the UserLessonStatus model
        with open(output_path, 'rb') as f:
            userLesson.watermarked_video.save(output_filename, File(f))
            userLesson.save()

        logger.info(f"generate_watermarked_video_task_fast lesson.video.url {userLesson.watermarked_video}")
        return lesson.video.url if lesson else None

    except Exception as e:
        logger.error(f"Error generating watermarked video: {str(e)}")
        return str(e)


def get_video_duration(input_path):
    """Get the duration of the video using FFmpeg."""
    command = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    duration = float(result.stdout)
    return duration

def generate_watermarked_video_fast(input_path, watermark_text, font_path, output_path, preset="veryfast", video_codec="libx264", resize=(1280, 720)):
    """
    Generate a watermarked video quickly using FFmpeg with dynamic watermark positioning.

    Args:
        input_path (str): Path to the input video file.
        watermark_text (str): Text to use as the watermark.
        font_path (str): Path to the font file.
        output_path (str): Path to save the output video file.
        preset (str): Encoding speed preset (e.g., "ultrafast", "superfast", "veryfast").
        video_codec (str): Video codec to use (e.g., "libx264" for H.264, "h264_nvenc" for NVIDIA).
        resize (tuple): Resize the video to (width, height). Example: (1280, 720) for 720p.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        duration = get_video_duration(input_path)
        interval = 20  # Change watermark position every 20 seconds

        # Define watermark positions with adjusted margins
        positions = [
            {"x": "(w-text_w)-350", "y": "200"},  # Top-right (moved 50px from right, 30px from top)
            {"x": "350", "y": "200"},  # Top-left (moved 50px from left, 30px from top)
            {"x": "(w-text_w)/2", "y": "(h-text_h)/2"},  # Center (unchanged)
            {"x": "350", "y": "(h-text_h)-200"},  # Bottom-left (moved 50px from left, 30px from bottom)
            {"x": "(w-text_w)-350", "y": "(h-text_h)-200"},  # Bottom-right (moved 50px from right, 30px from bottom)
        ]

        # Generate the drawtext filters for each interval
        drawtext_filters = []
        num_positions = len(positions)
        for i in range(int(duration // interval) + 1):
            start_time = i * interval
            end_time = (i + 1) * interval if (i + 1) * interval < duration else duration
            pos = positions[i % num_positions]  # Cycle through positions
            drawtext_filters.append(
                f"drawtext=text='{watermark_text}':fontfile={font_path}:fontsize=50:fontcolor=white:x={pos['x']}:y={pos['y']}:box=1:boxcolor=black@0.5:boxborderw=5:enable='between(t,{start_time},{end_time})'"
            )

        # Combine all drawtext filters into a single filter chain
        filter_chain = ",".join(drawtext_filters)

        # FFmpeg command to add a dynamic watermark
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_path,  # Input video
            '-vf', f"{filter_chain},scale={resize[0]}:{resize[1]}",  # Watermark and resize
            '-c:v', video_codec,  # Video codec
            '-preset', preset,  # Encoding speed preset
            '-c:a', 'copy',  # Copy audio stream without re-encoding
            '-y',  # Overwrite output file if it exists
            '-threads', '8',
            '-benchmark',  # Enable benchmarking
            '-report',  # Generate a detailed report
            output_path
        ]

        # Run the FFmpeg command
        subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        logger.info(f"Watermarked video generated successfully: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg command failed: {e.stderr.decode('utf-8')}")
        return False
    except Exception as e:
        logger.error(f"Error generating watermarked video: {e}")
        return False
@shared_task
def generate_watermarked_video_task_fast(video_path, user_first_name, user_last_name, user_phone_number, user_id, course_id, lesson_id):
    font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'Arial.ttf')
    logger.info(f"generate_watermarked_video_task_fast lesson.video.url {video_path} : {user_phone_number}")

    try:
        User = get_user_model()
        user_main = User.objects.get(id=user_id)
        logger.info(f"User retrieved: {user_main}")

        # Find the lesson associated with the video
        lesson = Lesson.objects.filter(id=lesson_id).first()
        if not lesson:
            logger.error(f"No lesson found for video_path: {video_path}")
            return None
        logger.info(f"Lesson retrieved: {lesson}")

        # Create or retrieve UserLessonStatus
        userLesson, created = UserLessonStatus.objects.get_or_create(
            user=user_main,
            lesson=lesson,
            defaults={
                # Add any default fields here if needed
            }
        )
        logger.info(f"UserLessonStatus retrieved or created: {userLesson}, created: {created}")

        # Watermark text
        watermark_text = f"{user_main.username} - {user_phone_number}"

        # Output file path
        output_filename = f"watermarked_{os.path.basename(video_path)}"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'watermarked_videos')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        # Generate the watermarked video quickly
        success = generate_watermarked_video_fast(
            input_path=video_path,
            watermark_text=watermark_text,
            font_path=font_path,
            output_path=output_path,
            preset="veryfast",  # Use a faster preset
            video_codec="libx264",  # Use H.264 for faster encoding
            resize=(1280, 720),  # Resize to 720p for faster processing
        )

        if not success:
            raise Exception("Failed to generate watermarked video")

        # Save the watermarked video to the UserLessonStatus model
        with open(output_path, 'rb') as f:
            userLesson.watermarked_video.save(output_filename, File(f))
            userLesson.save()

        logger.info(f"generate_watermarked_video_task_fast lesson.video.url {userLesson.watermarked_video} : {user_phone_number}")
        return lesson.video.url if lesson else None

    except Exception as e:
        logger.error(f"Error generating watermarked video: {str(e)}")
        return str(e)