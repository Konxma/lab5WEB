import { Module } from '@nestjs/common';
import { GadgetsModule } from '../gadgets/gadgets.module';
import { SharedModule } from '../shared/shared.module';
import { OrdersController } from './orders.controller';
import { OrdersService } from './orders.service';

@Module({
  imports: [GadgetsModule, SharedModule],
  controllers: [OrdersController],
  providers: [OrdersService],
})
export class OrdersModule {}
