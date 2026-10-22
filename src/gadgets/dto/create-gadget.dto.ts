import { IsInt, IsNotEmpty, IsNumber, IsString, Min } from 'class-validator';

export class CreateGadgetDto {
  @IsString()
  @IsNotEmpty()
  title!: string;

  @IsNumber({ maxDecimalPlaces: 2 })
  @Min(0)
  price!: number;

  @IsInt()
  @Min(0)
  warrantyMonths!: number;

  @IsString()
  @IsNotEmpty()
  cpu!: string;

  @IsInt()
  @Min(1)
  ramGb!: number;
}
