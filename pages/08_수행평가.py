# 설치 (터미널에서 한 번만 실행)
# pip install kagglehub[pandas-datasets]

import kagglehub
from kagglehub import KaggleDatasetAdapter

def load_first_tabular_file(dataset_ref: str):
    """
    dataset_ref 예: "matthieugimbert/french-bakery-daily-sales"
    함수는 데이터셋의 파일 목록을 확인하여 우선적으로 .csv/.parquet/.xlsx 파일을 찾아 로드합니다.
    """
    try:
        # 1) 데이터셋 파일 목록 확인
        files = kagglehub.list_files(dataset_ref)
        if not files:
            raise RuntimeError(f"No files found in dataset '{dataset_ref}'")

        # 2) 우선순위로 불러올 확장자 지정
        preferred_ext = [".csv", ".parquet", ".xlsx", ".xls", ".json"]
        chosen = None

        # 단순 매칭: 우선순위 확장자로 파일 찾기
        for ext in preferred_ext:
            for f in files:
                if f.lower().endswith(ext):
                    chosen = f
                    break
            if chosen:
                break

        # 만약 우선 확장자가 없다면 그냥 첫 파일 선택
        if not chosen:
            chosen = files[0]

        print(f"Loading file: {chosen}")

        # 3) load_dataset 호출
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            dataset_ref,
            chosen,
            # 필요 시 pandas kwargs 추가: e.g., pandas_kwargs={"encoding": "utf-8"}
        )

        print("Loaded dataframe shape:", df.shape)
        return df

    except Exception as e:
        # 친절한 에러 메시지
        print("Error while loading dataset:", str(e))
        print("\nTroubleshooting tips:")
        print("- 먼저 `kagglehub`가 설치되어 있는지 확인하세요.")
        print("- Kaggle 인증(토큰)이 필요할 수 있습니다. (예: ~/.kaggle/kaggle.json 또는 환경변수 KAGGLE_USERNAME/KAGGLE_KEY)")
        print("- 네트워크나 권한 문제인지 확인하세요.")
        raise

if __name__ == "__main__":
    dataset_ref = "matthieugimbert/french-bakery-daily-sales"
    df = load_first_tabular_file(dataset_ref)
    print("First 5 records:\n", df.head())
