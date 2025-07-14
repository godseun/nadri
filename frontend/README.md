# 프론트엔드 애플리케이션

이 프로젝트는 나들이 서비스의 프론트엔드 애플리케이션으로, 백엔드 API와 상호작용하는 채팅 인터페이스를 제공합니다.

## 사용된 기술 스택

- **React**: 사용자 인터페이스 구축을 위한 JavaScript 라이브러리.
- **TypeScript**: 정적 타입을 추가하여 JavaScript를 확장한 언어.
- **Sass (SCSS)**: 변수, 중첩, 믹스인과 같은 기능을 통해 CSS를 확장하는 CSS 전처리기.
- **React Markdown**: Markdown을 렌더링하기 위한 React 컴포넌트.
- **React Syntax Highlighter**: 코드 블록에 대한 구문 강조를 제공하는 라이브러리.

## 시작하기

프론트엔드 애플리케이션을 실행하기 위한 단계별 지침입니다.

### 필수 요구 사항

다음 소프트웨어가 시스템에 설치되어 있는지 확인하십시오:

- Node.js (LTS 버전 권장)
- npm (Node Package Manager) 또는 Yarn

### 설치

`frontend` 디렉토리로 이동하여 의존성을 설치합니다:

```bash
cd frontend
npm install
# 또는 yarn install
```

### 환경 변수

이 애플리케이션은 백엔드 API에 연결하기 위한 환경 변수를 필요로 합니다.

1.  `frontend` 디렉토리에 `.env` 파일을 생성합니다:

    ```
    # frontend/.env
    REACT_APP_API_URL=http://localhost:8000
    ```

    - **`REACT_APP_API_URL`**: 백엔드 API의 URL입니다. 백엔드가 다른 주소나 포트에서 실행 중인 경우 `http://localhost:8000`을 업데이트해야 합니다.

2.  `.env` 파일을 생성하거나 수정한 후에는 변경 사항을 적용하기 위해 개발 서버를 다시 시작해야 합니다.

### 애플리케이션 실행

`frontend` 디렉토리에서 다음 명령어를 실행하여 개발 서버를 시작합니다:

```bash
npm start
# 또는 yarn start
```

애플리케이션은 일반적으로 `http://localhost:3000`에서 브라우저에 열립니다.

## 프로젝트 구조

- `public/`: `index.html`, `favicon.svg`, `logo.svg`와 같은 정적 자산을 포함합니다.
- `src/`:
  - `App.tsx`: 메인 애플리케이션 컴포넌트.
  - `index.tsx`: React 애플리케이션의 진입점.
  - `App.scss`, `index.scss`, `_variables.scss`: 전역 및 컴포넌트별 스타일링을 위한 Sass 스타일시트.
  - `components/`: 재사용 가능한 React 컴포넌트.
    - `ThemeToggleButton.tsx`: 라이트 및 다크 테마 토글을 위한 컴포넌트.
    - `ChatInterface.tsx`: 메인 채팅 인터페이스 컴포넌트.
    - `Message.tsx`: 개별 채팅 메시지를 렌더링하기 위한 컴포넌트.
    - `MessageInput.tsx`: 채팅 입력 영역 및 전송 버튼을 위한 컴포넌트.
    - `ScrollToBottomButton.tsx`: 하단 스크롤 버튼을 위한 컴포넌트.
  - `context/`: 전역 상태 관리를 위한 React Context.
    - `ChatContext.tsx`: 채팅 관련 상태 및 함수를 자식 컴포넌트에 제공합니다.
  - `hooks/`: 커스텀 React 훅.
    - `useChat.ts`: 채팅 로직 및 상태 관리를 위한 커스텀 훅.
  - `reportWebVitals.ts`, `setupTests.ts`: 성능 보고 및 테스트 설정을 위한 유틸리티 파일.

## 사용 가능한 스크립트

프로젝트 디렉토리에서 다음을 실행할 수 있습니다:

- `npm start`: 개발 모드에서 앱을 실행합니다.
- `npm run build`: `build` 폴더에 프로덕션용 앱을 빌드합니다.
