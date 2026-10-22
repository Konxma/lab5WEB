import { Module } from '@nestjs/common';
import { SharedModule } from '../shared/shared.module';
import { GadgetsController } from './gadgets.controller';
import { GadgetsService } from './gadgets.service';

@Module({
  imports: [SharedModule],
  controllers: [GadgetsController],
  providers: [GadgetsService],
  exports: [GadgetsService],
})
export class GadgetsModule {}
