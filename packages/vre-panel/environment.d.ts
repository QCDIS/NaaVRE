declare global {
  namespace NodeJS {
    interface ProcessEnv {
      BASE_IMAGE_TAGS_URL: string;
    }
  }
}

export {}
