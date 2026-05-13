# 干涉条纹平面度分析器

这是一个 Python / FastAPI 项目，用于从干涉条纹图中估算平面度相关参数，重点面向**矩形孔径光学面**，例如六面平面转镜（hexagon scanning mirror）的单个反射面。

> 当前状态：工程原型。适合研发、验证、流程搭建；如果要作为正式计量工具，需要用原始干涉仪数据和可靠标准样品继续标定。

## 功能概览

### 1. Raw / Direct Fringe Mode

用于直接输入干涉条纹强度图。

功能包括：

- FFT carrier demodulation
- phase unwrapping
- 矩形孔径低阶面形拟合
- P-V、RMS、Power、Irregularity 估算
- 自动生成诊断报告图

### 2. Zygo Screenshot Audit Mode

用于已有 Zygo 截图的审查和归档。

功能包括：

- 裁剪 Zygo 截图中的 wavefront map
- 裁剪 colorbar
- 根据颜色条反推近似 wavefront map
- 用截图中的 P-V 作为校准值，估算显示图对应的 RMS 等参数

注意：这个模式不是独立计量，因为 P-V 是输入校准值。

## 诊断图示例

Raw fringe 模式会生成包含 ROI、wavefront map、residual map 和指标的诊断图：

![诊断图示例](docs/assets/example_diagnostic_report.png)

## 快速启动：Python 源码模式

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
uvicorn iflat.api:app --host 127.0.0.1 --port 8000
```

打开浏览器：

```text
http://127.0.0.1:8000/docs
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

## CLI 示例

### Raw / Direct Fringe Mode

```bash
iflat raw-fringe path/to/fringe.jpg \
  --bbox 108,116,208,199 \
  --wavelength-nm 633 \
  --out reports/example_raw
```

### Zygo Screenshot Audit Mode

```bash
iflat zygo-screenshot path/to/Zygo0.png \
  --map-bbox 122,136,748,710 \
  --colorbar-bbox 900,66,927,804 \
  --pv-waves 0.200 \
  --wavelength-nm 633 \
  --out reports/example_zygo
```

## API 接口

### `POST /analyze/raw-fringe`

用于直接条纹图分析。

字段：

- `file`：条纹图片
- `bbox`：可选，格式 `x1,y1,x2,y2`，建议对拍摄图片提供
- `wavelength_nm`：默认 `633.0`
- `values_are`：默认 `wavefront_error`

### `POST /audit/zygo-screenshot`

用于 Zygo 截图审查。

字段：

- `file`：Zygo 截图
- `map_bbox`：wavefront map 的位置，格式 `x1,y1,x2,y2`
- `colorbar_bbox`：colorbar 的位置，格式 `x1,y1,x2,y2`
- `calibration_pv_waves`：Zygo 截图上显示的 P-V，单位 waves
- `wavelength_nm`：默认 `633.0`

## Docker / Portainer

本项目可以打包成 Docker container，并通过 Portainer 部署成 Web Service。

本地构建：

```bash
docker build --network=host -t interferogram-flatness:0.1.0 .
docker run --rm -p 8000:8000 -e IFLAT_RUN_ROOT=/data/reports interferogram-flatness:0.1.0
```

Portainer 说明见：

[`docs/docker_portainer_deployment.md`](docs/docker_portainer_deployment.md)

## Windows 运行

Windows 下可以用 Python 源码模式或 Docker Desktop 模式运行。

说明见：

[`docs/windows_run_guide.md`](docs/windows_run_guide.md)

## 重要限制

- 如果输入不是原始干涉仪强度图，而是手机拍摄图或截图，结果只能作为趋势判断。
- 拍摄图会受透视、过曝、gamma、压缩和背景光影响。
- Zygo screenshot audit mode 依赖截图显示颜色和 P-V 校准，不是独立计量。
- Zernike-equivalent 输出还没有正式进入 public API。

## License

License 还未最终确定。正式对外复用前建议补充 License 文件。
