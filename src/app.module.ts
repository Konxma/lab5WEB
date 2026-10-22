import { Module } from '@nestjs/common';
import { ClothesModule } from './clothes/clothes.module';
import { OrdersModule } from './orders/orders.module';
import { SharedModule } from './shared/shared.module';

@Module({
  imports: [SharedModule, ClothesModule, OrdersModule],
})
export class AppModule {}
