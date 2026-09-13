# PS1-Muhan · Pricing a Promise

Muhan Chen · COMSCI/ECON 206 · Autumn 2026 Session 1

这份目录已经按作业要求搭好：**论文源码 + 可复现代码 + Hugging Face 游戏源码**。你自己上传即可。

## 你还需要做的事（按顺序）

1. **Overleaf 编译**
   - 把 `overleaf/` 整个文件夹打成 zip（不要包含上一级的 `.venv`）。
   - Overleaf → New Project → Upload Project → 上传这个 zip。
   - 主文件设为 `main.tex`，编译器 **pdfLaTeX**，编译两次以刷新参考文献。
   - 若正文超过 2 页，只删 `sections/proposal.tex` 的句子，不要删五个章节标题。
   - 作者邮箱我先写成 `mc956@duke.edu`，不对就在 `main.tex` 改。

2. **把 Figure 1 换成 diagrams.net 导出的 PDF（建议）**
   - 打开 https://app.diagrams.net ，载入 `overleaf/figures/ps1_teaser.drawio`。
   - File → Export as → PDF，覆盖 `overleaf/figures/ps1_teaser.pdf`。
   - 现在的 PDF 已能编译，但是作业要求提交 **可编辑 .drawio + 矢量 PDF**。

3. **插入两张考察照片**
   - 把 Week 2 用过的两张原图放到  
     `overleaf/figures/photo_tencent.jpg` 和 `overleaf/figures/photo_museum.jpg`。
   - 然后在 `overleaf/appendices/supporting.tex` 的 Appendix C 里取消注释 / 加上 `\includegraphics`。

4. **GitHub + Colab（你自己建）**
   - 新建仓库，名字用 `PS1-Muhan`。
   - 上传本目录（排除 `.venv/`、`.mpl/`）。
   - 用 Colab 打开 `cheap-talk-audit/notebooks/ps1_cheap_talk_audit.ipynb`，Run all，确认 seed 206 得到 +48/+24/+22/+18。
   - 把仓库 URL、Colab URL、**实际 commit** 填进 `overleaf/main.tex` 的三个 `\newcommand`。

5. **Hugging Face**
   - 把 `cheap-talk-audit/hf_space/index.html` 和 `README.md` 更新到现有 Space  
     https://huggingface.co/spaces/dku-comsci-econ206-2026/demo2  
     或新建一个 Static Space，再改论文里的 `\DemoLink`。
   - 浏览器无痕窗口玩完 12 轮，确认最后出现 Classroom debrief。

6. **周一手写反馈（作业禁止编造）**
   - 附录 B 只用了工作坊**官方提示**（grounding / testability），没有编 Rogerson 或同学的原话。
   - 如果你 Ed 上的手写 exit note 有一句具体评论，把它补进 `appendices/supporting.tex` 的 Monday 段。有就更分；没有也可以交。

7. **Canvas 提交（9 月 13 日 23:00）**
   - 编译好的 PDF：`Chen_Muhan_PS1_v1.pdf`（清单上也写了 `PS1-mc956-Muhan-Chen.pdf`，按老师最新文件名要求选一个，或两个都准备）。
   - Overleaf 源码 zip。
   - 代码快照 zip（`cheap-talk-audit/` + 说明，不要 `.venv`）。
   - 论文里的 GitHub / Colab / HF 链接必须能打开。

## 已经替你完成的内容

- 五节正文，延续 Week 2 Cheap-Talk Audit，不换题。
- 真实算过的数字：seed 206 与 JS 完全一致；`p*=0.6`；1000 个 seed 的均值。
- Python 引擎、单元测试、notebook、HF 学习模式、Draw.io 源文件、附录 A–E。
- 致谢里写了 Luyao Zhang、Ken Rogerson、Yiqiao Liu、Xinrong Sun。
- AI 使用已按作业要求披露。

## 不要改的事实标签

合成结果、占位概率 0.85/0.25、单一种子不是样本——正文已经写明。不要把 Monte Carlo 说成真人实验。
