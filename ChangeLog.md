
# [1.4.0] - 2025-12-20
### New Features
- **Standalone Subtitle**: 新增 `subtitle` 任务，支持不转码的 Stream Copy 软字慕封装。
- **Soft Subtitle Embedding**: `convert` 任务现在会自动探测并封装同名 `.srt`/`.ass` 字幕。
- **Multi-Audio Preservation**: 视频转码现在会保留所有音频流 (而不仅仅是第一条)。
- **Compatibility Mode**: `convert` 任务新增 `compatibility_mode` 参数，针对老旧设备提供最强兼容性 (Deinterlace, YUV420P, High@4.1, CFR)。

# [1.3.0] - 2025-12-20
### Architecture Refactor
- **Unified Interface**: 引入 `main.py` 作为统一入口，替代分散的 runner 脚本。
- **JSON Configuration**: 所有参数通过 JSON 文件配置 (`params/`)，支持 generic paths 模版。
- **Makefile Integration**: 引入 `Makefile` 管理依赖 (`make install`) 和 运行任务 (`make run`)。
- **Modular Runners**: 重构所有 Runner 接受参数对象，解耦硬编码路径。

### New Features
- **Video Merge**: 新增 `merge` 任务，支持基于 FFmpeg Stream Copy 的无损视频合并。
- **Timelapse**: 明确了 Timelapse 的 1-to-1 处理逻辑。

# [1.2.0] - 2025-12-11
支持多分辨率转码, 而不是固定720p
1. 用枚举类型, 包含720p, 1080p
2. 由于在转码时, 使用source_dir和target_dir, 不需要进行是否对已经转码的文件重新转码(当前代码中用"_720p"来区分的)
3. 增加一个选项, 标识完成转码后, 是否删除原文件, 默认为不删除
4. 生成中的文件名增加_processing, 后缀名保持不变, 在生成后, 再改名


# [1.1.0] - 2025-12-10
### Change
- 支持读取项目外部的绝对路, 以便直接读取系统其他路径(Nas挂载磁盘)下文件的需求
- 在batch_runner_media_converter进行视频压缩时, 保持输出文件夹保持输入文件夹的目录结构
