import { Module } from '@nestjs/common';
import { GadgetsModule } from './gadgets/gadgets.module';
import { HomeModule } from './home/home.module';
import { OrdersModule } from './orders/orders.module';
import { SharedModule } from './shared/shared.module';

@Module({
  imports: [HomeModule, SharedModule, GadgetsModule, OrdersModule],
})
export class AppModule {}
