
# [1.2.0] - 2025-12-11
支持多分辨率转码, 而不是固定720p
1. 用枚举类型, 包含720p, 1080p
2. 由于在转码时, 使用source_dir和target_dir, 不需要进行是否对已经转码的文件重新转码(当前代码中用"_720p"来区分的)
3. 增加一个选项, 就是完成转码后, 是否删除原文件, 默认为不删除
4. 生成中的文件名增加_processing, 后缀名保持不变, 在生成后, 再改名

主要需要修改
runner/batch_runner_media_converter.py
service/media_process/video_processor.py

# [1.1.0] - 2025-12-10
### Change
- 支持读取项目外部的绝对路, 以便直接读取系统其他路径(Nas挂载磁盘)下文件的需求
- 在batch_runner_media_converter进行视频压缩时, 保持输出文件夹保持输入文件夹的目录结构

比如:
输入文件夹
 /1.mp4
 /serial2/2.mp4
 /collection3/serial3/3.mp4

输出文件夹
 /1.mp4
 /serial2/2.mp4
 /collection3/serial3/3.mp4