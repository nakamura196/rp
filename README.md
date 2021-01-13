# Rectangle Packing with IIIF Curation

IIIFキュレーションリストを、一枚の画像に変換する（個々のアイテムを一枚の画像に敷き詰める）プログラムです。

## Install

Requirements:

- Python 3

Install latest release:

```
pip install -r requirements.txt
```

## Usage

例えば、以下のように実行してください。

```
python main.py https://utda.github.io/tenjiroom/genelib_vm2020-01.json
```

実行後、 `data/data.json` にIIIFマニフェストファイルが出力されます。

オプションは、以下からご確認ください。

```
python main.py -h
```

## Example

http://mirador.cultural.jp/?manifest=https://api.jsonbin.io/b/5fff00eb8aa7af359da98ed1;https://api.jsonbin.io/b/5ffea04568f9f835a3de9857/1;https://api.jsonbin.io/b/5fff023f8aa7af359da98f2f
