支持多分辨率转码, 而不是固定720p
1. 用枚举类型, 包含720p, 1080p
2. 由于在转码时, 使用source_dir和target_dir, 不需要进行是否对已经转码的文件重新转码(当前代码中用"_720p"来区分的)
3. 增加一个选项, 就是完成转码后, 是否删除原文件, 默认为不删除
4. 生成中的文件名后缀为.processing, 在生成后, 再改名

主要需要修改
runner/batch_runner_media_converter.py
service/media_process/video_processor.py