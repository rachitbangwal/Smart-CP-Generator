declare module 'pdf-parse' {
  interface PDFData {
    text: string;
    numpages: number;
    info: {
      Title?: string;
      Author?: string;
      Subject?: string;
      Keywords?: string;
      Creator?: string;
      Producer?: string;
      CreationDate?: Date;
      ModDate?: Date;
    };
    metadata: any;
    version: string;
  }

  interface PDFOptions {
    pagerender?: (pageData: any) => string;
    max?: number;
    version?: string;
    throwOnDataErrors?: boolean;
  }

  function parse(dataBuffer: Buffer, options?: PDFOptions): Promise<PDFData>;

  export = parse;
}
