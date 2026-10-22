import { Global, Module } from '@nestjs/common';
import { STORE_CONFIG, appConfigProvider } from './config/app-config.provider';
import { FEE_CALCULATOR, feeCalculatorProvider } from './config/fee-calculator.provider';
import { RequestIdService } from './request-id.service';
import { RequestTraceService } from './request-trace.service';
import { SlugService } from './slug.service';

@Global()
@Module({
  providers: [SlugService, RequestIdService, RequestTraceService, appConfigProvider, feeCalculatorProvider],
  exports: [SlugService, RequestIdService, RequestTraceService, STORE_CONFIG, FEE_CALCULATOR],
})
export class SharedModule {}
